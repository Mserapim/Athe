from django.db.models import Count, Q

from django.core.exceptions import ValidationError

from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import getLogger, get_json_engine, DateUtils

from standard.models import Choice
from engine.mq.models import Task
from rh.models import (
    MovimentacaoSubstituicao,
    MovesSubstitutionsConsolidated,
    ServidorLotacao,
    Servidor as Employee,
)

from rh.gfp.api.payroll import GFPPayroll

from rh.gratifications_manager.tasks_cumulative_exercises import (
    autorizate_mov_sub_task,
    consolidate_able_to_pay_employee_task,
    desconsolidate_item_task,
    calculate_consolidated_task,
    defer_consolidated_task,
)

from rh.gratifications_manager.cumulative_exercices_utils import (
    validar_periodo_vigente_exerc_cumul_subs,
)

log = getLogger(__name__)
json_engine = get_json_engine()


class GMCumulativeExercises(RestfulDRY):

    _model = MovimentacaoSubstituicao

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor_substituido__pessoa_fisica__nome__icontains",
    )

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    exclude_fields = ["modified_by", "created_by", "created_at", "modified_at"]

    @login_required("JSON")
    def json(self, args=[]):
        q_classif_lotacao = Choice.objects.filter(
            app_label="rh", name="CLASSIFICACAO_LOTACAO"
        )
        classif_lotacao = [
            {"id": x.value, "titulo": x.label} for x in q_classif_lotacao
        ]

        params = {
            "classif_lotacao": classif_lotacao,
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(
            f"Ext._create('rh.gratifications_manager.cumulative_exercises.Manage', {params})"
        )

    def get_query(self):
        return super().get_query().order_by("servidor", "-data_inicio", "-data_fim")

    def get_status_msg_icon(self, instance):
        if (
            instance.substitutions_consolidated.exists()
            and instance.substitutions_consolidated.first().gcpp
            and instance.substitutions_consolidated.first().gcpp.status == "pago"
        ) or instance.paid_out:
            return ["Pago", "icon-fopag icon-cash"]
        elif instance.indeferido:
            return ["Indeferido", "icon-fopag icon-status-block"]
        elif instance.consolidated:
            return ["Consolidado", "icon-fopag icon-status-offline"]
        elif instance.able_to_pay:
            return ["Apto para pgto", "icon-fopag icon-status"]
        else:
            return ["Inapto para pgto", "icon-fopag icon-status-busy"]

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        status_msg, icon = self.get_status_msg_icon(instance)
        icons.append(
            {
                "iconCls": icon,
                "title": status_msg,
                "alt": status_msg,
            }
        )

        return icons

    @classmethod
    def get_qtd_dias(self, instance):
        if instance.financial_effect_date_start:
            dt_start = instance.financial_effect_date_start
        else:
            dt_start = instance.data_inicio

        if instance.financial_effect_date_end:
            dt_end = instance.financial_effect_date_end
        else:
            dt_end = instance.data_fim

        if dt_start and dt_end:
            return str(((dt_end - dt_start).days) + 1)
        else:
            return ""

    def get_periodo_pgto(self, instance):
        if instance.pay_month and instance.pay_year:
            return f"{instance.pay_month}/{instance.pay_year}"
        else:
            return ""

    @classmethod
    def get_lotacao_mais_antiga(self, lotacoes):
        return lotacoes.order_by("data_vigencia_inicio").first()

    @classmethod
    def get_lotacao_from_q(self, q):
        if q.count() == 1:
            q_lotacao = q.first().lotacao
            return str(q_lotacao) if q_lotacao else ""
        else:
            return str(self.get_lotacao_mais_antiga(q))

    @classmethod
    def get_titularidade(self, servidor):
        lotacoes = ServidorLotacao.objects.filter(
            servidor=servidor, ativo=True, designacao=True
        )

        q = lotacoes.filter(main=True)
        if q.exists():
            return self.get_lotacao_from_q(q)

        q = lotacoes.filter(owner=True)
        if q.exists():
            return self.get_lotacao_from_q(q)

        return self.get_lotacao_from_q(q) if q.exists() else ""

    @classmethod
    def get_cumulativa(self, instance):
        if instance.designation_substituted:
            return str(instance.designation_substituted.lotacao)
        else:
            return ""

    def model_to_dict(self, instance):
        params = super(GMCumulativeExercises, self).model_to_dict(instance)
        params.update(
            {
                "icons": self.get_icons(instance),
                "qtd_dias": self.get_qtd_dias(instance),
                "periodo_pgto": self.get_periodo_pgto(instance),
                "titularidade": self.get_titularidade(instance.servidor),
                "cumulativa": self.get_cumulativa(instance),
                "data_pgto_inicio": instance.financial_date_start,
                "data_pgto_fim": instance.financial_date_end,
                "periodo": (
                    ""
                    if instance.periodo_cumul_subs is None
                    else str(instance.periodo_cumul_subs)
                ),
            }
        )

        return params

    def do_put_single(self, pk=None):
        """Atualiza uma instância."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            params = self.get_params(self.request.PUT, check_case=True)
            inst = self.Model.objects.get(pk=pk)
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o item que deseja atualizar. pk: %s model: %s ctr: %s"
                % (pk, self.Model.__name__, self.__class__.__name__)
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            if self.can_update_fields_values is not None:
                params = {
                    k: v
                    for k, v in list(params.items())
                    if k in self.can_update_fields_values
                }

            self.fill_instance_values(inst, params)
            try:
                if self.use_full_clean:
                    inst.full_clean()

                inst.financial_effect_date_start = DateUtils.str_to_date(
                    params["data_pgto_inicio"]
                )
                inst.financial_effect_date_end = DateUtils.str_to_date(
                    params["data_pgto_fim"]
                )

                inst.save()
                self.fill_instance_m2m(inst, params)
            except ValidationError as e:
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistido com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    @login_required("JSON")
    def able_to_pay_selected(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            try:
                movs_ids = self.request.POST.getlist("ids")
                Task.start(
                    autorizate_mov_sub_task,
                    description=f"Autorizando pagamentos de {len(movs_ids)} exercícios cumulativos.",
                    user=self.request.user.id,
                    movs_ids=movs_ids,
                )

                obj["message"] = (
                    f"Autorizando pagamentos dos exercícios cumulativos selecionados."
                )
            except:
                obj["success"] = False
                obj["message"] = (
                    f"ERRO ao autorizar pagamentos dos exercícios cumulativos selecionados"
                )

        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def indeferir_selecionados(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            try:
                movs_ids = self.request.POST.getlist("ids")
                mov_subs = MovimentacaoSubstituicao.objects.filter(
                    pk__in=movs_ids
                ).update(indeferido=True)

                obj["message"] = (
                    f"Exercícios cumulativos selecionados foram indeferidos."
                )
            except:
                obj["success"] = False
                obj["message"] = (
                    f"ERRO ao tentar indeferir os exercícios cumulativos selecionados"
                )

        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def consolidate_able_to_pay(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            try:
                validacao_periodo = validar_periodo_vigente_exerc_cumul_subs()
                if validacao_periodo["success"] == False:
                    obj["success"] = False
                    obj["message"] = validacao_periodo["msg"]
                else:
                    search_field = self.request.POST.get("search_field")
                    dt_start = self.request.POST.get("dt_start")
                    dt_end = self.request.POST.get("dt_end")

                    movs = MovimentacaoSubstituicao.objects.filter(
                        able_to_pay=True,
                        consolidated=False,
                        defer=False,
                    )

                    if search_field:
                        movs = movs.filter(servidor__matricula=search_field)

                    if dt_start:
                        dt_start = dt_start[0:10]
                        movs = movs.filter(data_inicio__gte=dt_start)

                    if dt_end:
                        dt_end = dt_end[0:10]
                        movs = movs.filter(data_fim__lte=dt_end)

                    if movs.count() == 0:
                        obj["success"] = False
                        obj["message"] = (
                            f"Não há exercícios cumulativos aptos para pagamentos"
                        )
                    else:
                        movs_employee = (
                            movs.values("servidor")
                            .annotate(count=Count("servidor"))
                            .order_by()
                        )
                        for mov_employee in movs_employee:
                            employee = Employee.objects.get(pk=mov_employee["servidor"])
                            employee_movs_ids = [
                                mov.pk for mov in movs.filter(servidor=employee)
                            ]

                            Task.start(
                                consolidate_able_to_pay_employee_task,
                                description=f"Consolidando cumulativos do servidor {employee}",
                                user=self.request.user.id,
                                employee_id=employee.pk,
                                employee_movs_ids=employee_movs_ids,
                                periodo_cumul_subs_id=validacao_periodo["periodo"].pk,
                            )

                        obj["message"] = (
                            f"Iniciando consolidação dos cumulativos aptos a pagamento."
                        )
            except:
                obj["success"] = False
                obj["message"] = f"ERRO ao consolidar cumulativos aptos a pagamento."

        self.response.write(json_engine.encode(obj))

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = []
        for record in query:
            rst.append(
                {
                    "substituto_matricula": record.servidor.matricula,
                    "substituto_nome": record.servidor.pessoa_fisica.nome,
                    "titularidade": self.get_titularidade(record.servidor),
                    "subtituido_matricula": record.servidor_substituido.matricula,
                    "subtituido_nome": record.servidor_substituido.pessoa_fisica.nome,
                    "cumulativa": self.get_cumulativa(record),
                    "data_inicio": record.data_inicio,
                    "data_fim": record.data_fim,
                    "qtd_dias": self.get_qtd_dias(record),
                    "periodo_pgto": self.get_periodo_pgto(record),
                    "parcelas_pgto": (
                        record.payment_installments
                        if record.payment_installments is not None
                        else ""
                    ),
                    "gedoc": record.gedoc if record.gedoc is not None else "",
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class GMCumulativeExercisesConsolidated(RestfulDRY):

    _model = MovesSubstitutionsConsolidated

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "employee__matricula__iexact",
        "employee__pessoa_fisica__nome__icontains",
    )

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.cumulative_exercises_consolidated.Manage")'
        )

    def get_query(self):
        q = super().get_query().order_by("employee", "-defer", "-days_consolidated")

        return q

    def model_to_dict(self, instance):
        params = super(GMCumulativeExercisesConsolidated, self).model_to_dict(instance)
        params.update(
            {
                "icons": self.get_icons(instance),
                "titularidade": GMCumulativeExercises.get_titularidade(
                    instance.employee
                ),
                "periodo_pgto": self.get_periodo_pgto(instance),
                "payroll_applied": self.get_payroll(instance),
            }
        )

        return params

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        status_msg = self.get_status_msg(instance)
        info_msg = self.get_info_msg(instance)
        icons.append(
            {
                "iconCls": self.get_info_icon(instance),
                "title": info_msg,
                "alt": info_msg,
            }
        )
        icons.append(
            {
                "iconCls": self.get_status_icon(instance),
                "title": status_msg,
                "alt": status_msg,
            }
        )

        return icons

    def get_status_icon(self, instance):
        if instance.gcpp and instance.gcpp.status == "pago":
            return "icon-fopag icon-cash"
        elif instance.defer:
            return "icon-fopag icon-status"
        else:
            return ""

    def get_status_msg(self, instance):
        if instance.gcpp and instance.gcpp.status == "pago":
            return "Pago"
        elif instance.defer:
            return "Deferido"
        else:
            return ""

    def get_info_icon(self, instance):
        return "icon-esocial icon-balloon-exclamation" if instance.info else ""

    def get_info_msg(self, instance):
        return instance.info if instance.info else ""

    def get_periodo_pgto(self, instance):
        if instance.paycheck_applied:
            return f"{instance.paycheck_applied.folha.periodo.mes}/{instance.paycheck_applied.folha.periodo.ano}"
        else:
            return ""

    def get_payroll(self, instance):
        return str(instance.paycheck_applied.folha) if instance.paycheck_applied else ""

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = []
        for record in query:
            rst.append(
                {
                    "substituto_matricula": record.employee.matricula,
                    "substituto_nome": record.employee.pessoa_fisica.nome,
                    "titularidade": GMCumulativeExercises.get_titularidade(
                        record.employee
                    ),
                    "qtd_dias": record.days_consolidated,
                    "periodo_pgto": self.get_periodo_pgto(record),
                    "pago": "Sim" if record.paid_out else "Não",
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    @login_required("JSON")
    def desconsolidated_mov_sub_cons(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        try:
            mov_sub_consolidated_id = self.request.POST.get("mov_sub_consolidated_id")
            mov_sub_cons = MovesSubstitutionsConsolidated.objects.get(
                pk=mov_sub_consolidated_id
            )

            if mov_sub_cons.paid_out:
                obj["success"] = False
                obj["message"] = (
                    f"Não é permitido desconsolidar um registro que já está pago."
                )
            else:
                Task.start(
                    desconsolidate_item_task,
                    description=f"Desconsolidando exercícios cumulativos: {mov_sub_cons}",
                    user=self.request.user.id,
                    mov_sub_consolidated_id=mov_sub_consolidated_id,
                )

                obj["message"] = (
                    f"Iniciando desconsolidação do exercício cumulativo consolidado."
                )
        except:
            obj["success"] = False
            obj["message"] = (
                f"ERRO ao desconsolidar exercício cumulativo consolidado: {mov_sub_cons}."
            )

        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def calculate_consolidated(self, *args):
        obj = {
            "success": True,
            "message": "",
        }

        try:
            mov_sub_consolidated_id = self.request.POST.get("mov_sub_consolidated_id")
            mov_sub_cons = MovesSubstitutionsConsolidated.objects.get(
                pk=mov_sub_consolidated_id
            )

            Task.start(
                calculate_consolidated_task,
                description=f"Calculando exercícios cumulativos consolidado: {mov_sub_cons}",
                user=self.request.user.id,
                mov_sub_consolidated_id=mov_sub_consolidated_id,
            )

            obj["message"] = f"Iniciando cálculo do exercício cumulativo consolidado."
        except:
            obj["success"] = False
            obj["message"] = (
                f"ERRO ao calcular exercício cumulativo consolidado: {mov_sub_cons}."
            )

        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def defer_consolidated(self, *args):
        success = True
        message = ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            success = False
            message = f"Você não tem permissão para deferir o cumulativo consolidado"
        else:
            consolidated_ids = self.request.POST.getlist("consolidated_ids")

            if consolidated_ids[0] == "all":
                movs = MovesSubstitutionsConsolidated.objects.filter(
                    defer=False
                ).exclude((Q(value_calculated=None) | Q(value_calculated=0)))
            else:
                movs = MovesSubstitutionsConsolidated.objects.filter(
                    pk__in=consolidated_ids
                )

            for mov_sub_cons in movs:
                if mov_sub_cons.defer:
                    success = False
                    message = f"""
                    O exercício cumulativo consolidado escolhido já está deferido.
                    """
                elif mov_sub_cons.value_calculated in [None, 0]:
                    success = False
                    message = f"""
                    O exercício cumulativo consolidado escolhido ainda não foi calculado.
                    É necessário primeiro realizar o cálculo para depois poder deferir.
                    """
                else:
                    Task.start(
                        defer_consolidated_task,
                        description=f"Deferindo cumulativo consolidado: {mov_sub_cons}",
                        user=self.request.user.id,
                        mov_sub_id=mov_sub_cons.pk,
                    )

                    rst["message"] = (
                        f"Deferindo cumulativo consolidado: {mov_sub_cons}."
                    )

        rst = {
            "success": success,
            "message": message,
        }
        self.response.write(json_engine.encode(rst))


class GMCumulativeExercisesConsolidatedSubstitutions(RestfulDRY):

    _model = MovimentacaoSubstituicao

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
    )

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    exclude_fields = ["modified_by", "created_by", "created_at", "modified_at"]

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Manage")'
        )

    def model_to_dict(self, instance):
        params = super(
            GMCumulativeExercisesConsolidatedSubstitutions, self
        ).model_to_dict(instance)
        params.update(
            {
                "qtd_dias": GMCumulativeExercises.get_qtd_dias(instance),
                "titularidade": GMCumulativeExercises.get_titularidade(
                    instance.servidor
                ),
                "cumulativa": GMCumulativeExercises.get_cumulativa(instance),
            }
        )

        return params

    def get_query(self):
        return super().get_query().order_by("servidor", "-data_inicio", "-data_fim")


class GMCumulativeExercisesConsolidatedPayroll(GFPPayroll):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.cumulative_exercises_consolidated.PayrollManage")'
        )

    def get_query(self):
        query = super(GMCumulativeExercisesConsolidatedPayroll, self).get_query()
        return query.filter(status__in=[1, 2])

    def do_put(self, pk=None):
        rst = {
            "success": True,
            "message": "",
        }

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst["success"] = False
            rst["message"] = (
                f"Você não tem permissão para deferir o cumulativo consolidado."
            )
        else:
            consolidated_ids = self.request.PUT.getlist("consolidated_ids")

            if consolidated_ids[0] == "all":
                movs_sub = MovesSubstitutionsConsolidated.objects.filter(
                    paid_out=False
                ).exclude(
                    Q(value_calculated=None) | Q(value_calculated=0),
                )
                consolidated_ids = [diff.id for diff in movs_sub]

            for mov_id in consolidated_ids:
                mov_sub = MovesSubstitutionsConsolidated.objects.get(pk=mov_id)

                Task.start(
                    defer_consolidated_task,
                    description=f"Deferindo cumulativo consolidado: {mov_sub}",
                    user=self.request.user.id,
                    mov_sub_id=mov_sub.pk,
                    payroll_id=self.request.PUT["folha"],
                )

                rst["message"] = f"Deferindo cumulativo consolidado: {mov_sub}."

        return rst
