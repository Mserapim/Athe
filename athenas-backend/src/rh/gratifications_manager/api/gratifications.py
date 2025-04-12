import datetime
import json

from django.db.models import Case, When, CharField, Q

from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.decorator import login_required
from contrib.utils import get_json_engine, getLogger
from contrib.daterange import NewDateRange

from rh.gfp.models import Evento as Event, Folha as Payroll
from rh.models import Employee, WorkplaceConfigTag
from standard.models import Choice
from engine.mq.models import Task

from rh.api.employee import RHEmployeeRestful
from rh.gratifications_manager.gm_utils import *
from rh.gfp.gcpp_utils import criar_gcpp

from rh.gratifications_manager.tasks_gratifications import conferir_gratificacoes_task

json_engine = get_json_engine()
log = getLogger(__name__)


def departament_verify():
    if (
        get_current_user().has_perm("afastamento.ver_membros")
        and get_current_user().has_perm("afastamento.ver_servidores") is False
    ):
        return "expediente"
    return "rh"


class GMGratifications(RHEmployeeRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.gratifications.Manage", {departament: "%s"})'
            % departament_verify
        )


class WorkplaceTag(RestfulDRY):
    _model = Event

    PRIORITY = ["03000", "13600", "07600"]

    def get_event(self, tag):
        choice = Choice.objects.filter(
            app_label="rh", name="WORKPLACE_TAG", value=tag.tag
        ).first()
        return Event.objects.filter(numero=choice.description).first()

    def get_payroll(self, year, month):
        return Payroll.objects.filter(
            tipo_folha__titulo="NORMAL", periodo__ano=year, periodo__mes=month
        )

    def get_icons_event(self, conferencia_servidor, pgto_servidor):
        obj = []
        if pgto_servidor["pgto"]:
            title = "Pago"
            obj.append(
                {
                    "iconCls": "icon-fopag icon-cash",
                    "title": title,
                    "alt": title,
                }
            )

        if pgto_servidor["origem"] == "folhaevento":
            txt_tipo_insercao = Choice.objects.get(
                app_label="gfp",
                name="ENTRY_INSERTION_TYPE",
                value=pgto_servidor["tipo_insercao"],
            ).label
            title = f"Origem pgto: contra-cheque - {txt_tipo_insercao}"
            obj.append(
                {
                    "iconCls": "icon-fopag icon-money-pencil",
                    "title": title,
                    "alt": title,
                }
            )

        if conferencia_servidor.exists():
            title = "Conferido"
            obj.append(
                {
                    "iconCls": "icon-fopag icon-notebook-plus",
                    "title": title,
                    "alt": title,
                }
            )

        return obj

    def do_filter(self, query, force_filter=None):
        def fn(f):
            return {f.get("property"): self._filter_eval_value(f.get("value"))}

        try:
            flist = None
            if not force_filter:
                flist = json.loads(self.get_params().get("filter", "[]"))
            else:
                flist = force_filter
        except KeyError as e:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % e
            )
        except Exception as e:
            log.exception(e)
            raise (e)
        else:
            workplaces = fn(flist[0])["workplace__in"]

            dt_range = NewDateRange.range_from_month(
                int(self.get_params().get("year", datetime.date.today().year)),
                int(self.get_params().get("month", datetime.date.today().month)),
            )
            dt_range_inicio = dt_range[0]
            dt_range_fim = dt_range[1]

            q_workplace_config_tag = WorkplaceConfigTag.objects.filter(
                workplace__pk__in=workplaces
            ).exclude(
                Q(start_validity__gt=dt_range_fim)
                | (~Q(end_validity=None) & Q(end_validity__lt=dt_range_inicio))
            )

            choices = Choice.objects.filter(
                app_label="rh",
                name="WORKPLACE_TAG",
                value__in=[x.tag for x in q_workplace_config_tag],
            )

            query = query.filter(
                Q(numero__in=[x.description for x in choices]) | Q(numero="07600")
            )

        return query

    def get_query(self):
        """:returns: QuerySet com todas instâncias de Model."""

        return self.Model.objects.filter()

    def do_sort(self, query):
        return super().do_sort(query)

    def do_sort_tags(self, query):
        """
        Função que ordena as WORKPLACE_TAGS conforme a prioridade, a list de prioridades é uma constante que reflete as tags que devem aparecer primeiro,
        as demais tags aparecerão conforme seu peso descrito no modelo Choice, ajustado em ordem descrescente, ou seja, do maior para o menor.
        :returns: QuerySet com instâncias ordenadas
        """
        self.ICONS = []

        choices = Choice.objects.filter(app_label="rh", name="WORKPLACE_TAG").order_by(
            "-order_weight"
        )
        choices = ["%s" % t for t in choices.values_list("description", flat=True)]
        for i in self.PRIORITY:
            if i in choices:
                choices.remove(i)

        order_list = self.PRIORITY + choices
        query = query.annotate(
            position=Case(
                *[
                    When(**{"numero": val}, then=pos)
                    for pos, val in enumerate(order_list)
                ],
                output_field=CharField(),
            ),
        )
        return query.order_by("position")

    def do_get(self, pk=None):
        """Executa uma requisição GET

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância ou conjunto de instâncias.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        if pk is not None:
            rst = super().do_get(pk)
        else:
            try:
                query = self._model.objects.filter()
                if "filter" in self.request.GET:
                    query = self.do_filter(query)

                query = self.do_sort_tags(query)

                query = self.filtrar_conferencia(query)

                query = self.do_page(query)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                log.exception(str(e))
                rst.update(message=str(e))
            else:
                try:
                    rst.update(count=len(query))
                    rst.update(
                        {
                            "collection": [
                                self.model_to_dict(record) for record in query
                            ],
                            "success": True,
                            "message": "Processado com sucesso!",
                        }
                    )
                except Exception as e:
                    log.exception(str(e))
                    rst.update(message=str(e))

        return rst

    def filtrar_conferencia(self, query):
        servidor_id = self.request.GET.get("employee", None)
        filtro_conferencia = self.request.GET.get("filtro_conferencia", "todos")
        if servidor_id and filtro_conferencia != "todos":
            servidor = Employee.objects.get(pk=servidor_id)
            choices = Choice.objects.filter(
                app_label="rh", name="WORKPLACE_TAG"
            ).order_by("-order_weight")
            choices = ["%s" % t for t in choices.values_list("description", flat=True)]
            eventos = Event.objects.filter(numero__in=choices)
            q_cpp = ControlePagamentoPessoal.objects.filter(
                servidor=servidor, evento__in=eventos
            )

            date = datetime.date.today()

            periodo_ano = (
                date.year
                if not self.request.GET.get("year", None)
                else int(self.request.GET.get("year"))
            )
            if periodo_ano not in [None, "TODOS"]:
                q_cpp = q_cpp.filter(periodo_ano=periodo_ano)

            periodo_mes = (
                date.month
                if not self.request.GET.get("month", None)
                else int(self.request.GET.get("month"))
            )
            if periodo_mes not in [None, "0"]:
                q_cpp = q_cpp.filter(periodo_mes=periodo_mes)

            if filtro_conferencia == "conferido":
                if q_cpp.count() == 0:
                    query = query.filter(pk__in=[])
                else:
                    evento_ids = [gcpp.evento.pk for gcpp in q_cpp]
                    query = query.filter(pk__in=evento_ids)

            if filtro_conferencia == "nao_conferido":
                if q_cpp.count() == 0:
                    query = query.filter()
                else:
                    evento_ids = [gcpp.evento.pk for gcpp in q_cpp]
                    query = query.exclude(pk__in=evento_ids)

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gratifications_manager.gratifications.workplace_tag.Manage")'
        )

    def model_to_dict(self, instance):
        params = super(WorkplaceTag, self).model_to_dict(instance)

        date = datetime.date.today()
        year = (
            date.year
            if not self.request.GET.get("year", None)
            else int(self.request.GET.get("year"))
        )
        month = (
            date.month
            if not self.request.GET.get("month", None)
            else int(self.request.GET.get("month"))
        )
        employee = Employee.objects.filter(
            pk=self.request.GET.get("employee", None)
        ).first()

        conferencia_servidor = verificar_conferencia_servidor(
            employee, instance, year, month
        )
        pgto_servidor = verificar_pgto_servidor(employee, instance, year, month)
        payroll = self.get_payroll(year, month)

        params.update(
            {
                "calculate_days": calcular_dias_membro(
                    employee, payroll, instance, pgto_servidor
                ),
                "icons": self.get_icons_event(conferencia_servidor, pgto_servidor),
                "evento_numero": instance.numero,
                "servidor_id": employee.pk if employee else "",
                "periodo_ano": year,
                "periodo_mes": month,
            }
        )

        return params

    @login_required("JSON")
    def conferir_gratificacao(self, *args):
        obj = {
            "success": False,
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
                periodo_ano = self.request.POST.get("periodo_ano")
                periodo_mes = self.request.POST.get("periodo_mes")
                payroll = buscar_folha(periodo_ano, periodo_mes)

                if payroll.exists() is False:
                    obj[
                        "message"
                    ] = f"""Não há folha aberta no período selecionado.
                    Conferências só podem ser iniciadas após abertura da competência pelo Departamento de Folha."""
                else:
                    servidor = Servidor.objects.get(
                        pk=self.request.POST.get("servidor_id")
                    )
                    evento = Event.objects.get(
                        numero=self.request.POST.get("evento_numero")
                    )

                    conferencia_servidor = verificar_conferencia_servidor(
                        servidor, evento, periodo_ano, periodo_mes
                    )

                    if conferencia_servidor.exists():
                        if conferencia_servidor.first().status == "pago":
                            obj[
                                "message"
                            ] = f"""O registro de gratificação selecionado já está conferido e pago.
                            Não é possível realizar nenhuma ação no registro selecionado."""
                        else:
                            obj["message"] = (
                                f"O registro de gratificação já está conferido."
                            )
                    else:
                        qtd_dias = self.request.POST.get("qtd_dias")
                        if qtd_dias != "-":
                            criar_gcpp(
                                servidor,
                                evento,
                                qtd_dias,
                                periodo_ano,
                                periodo_mes,
                                Servidor.objects.get(user=get_current_user()).pk,
                            )

                        obj["success"] = True
                        obj["message"] = (
                            f"O registro de gratificação foi marcado como conferido com sucesso."
                        )
            except:
                obj["message"] = "Erro no processamento para marcação de conferido."

        self.response.write(json_engine.encode(obj))

    @login_required("JSON")
    def conferir_lista_gratificacoes(self, *args):
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
                Task.start(
                    conferir_gratificacoes_task,
                    description=f"Processamento para conferência de gratificações.",
                    user=self.request.user.id,
                    gratificacoes=json.loads(self.request.POST.get("gratificacoes")),
                    conferido_por_id=Servidor.objects.get(user=get_current_user()).pk,
                )

                obj["message"] = (
                    "Iniciando processamento para conferência das gratificações (somente os registros válidos serão processados)."
                )
            except:
                obj["success"] = False
                obj["message"] = "Erro no processamento para marcação de conferido."

        self.response.write(json_engine.encode(obj))

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
            try:
                f = json.loads(self.request.GET.get("filter"))
            except Exception:
                f = []
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)

        query = self.remove_projection(query)
        query = self.filtrar_conferencia(query)

        date = datetime.date.today()
        year = (
            date.year
            if not self.request.GET.get("year", None)
            else int(self.request.GET.get("year"))
        )
        month = (
            date.month
            if not self.request.GET.get("month", None)
            else int(self.request.GET.get("month"))
        )
        employee = Employee.objects.filter(
            pk=self.request.GET.get("servidor_id", None)
        ).first()

        rst = []
        for record in query:
            conferencia_servidor = verificar_conferencia_servidor(
                employee, record, year, month
            )
            pgto_servidor = verificar_pgto_servidor(employee, record, year, month)
            payroll = self.get_payroll(year, month)

            icons_gratif = self.get_icons_event(conferencia_servidor, pgto_servidor)

            gratif_pgto = "Não"
            gratif_origem_pgto = "-"
            gratif_conferencia = "Não"
            for icon_reg in icons_gratif:
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Pago":
                    gratif_pgto = "Sim"
                if "alt" in icon_reg.keys() and "Origem pgto" in icon_reg["alt"]:
                    gratif_origem_pgto = icon_reg["alt"]
                if "alt" in icon_reg.keys() and icon_reg["alt"] == "Conferido":
                    gratif_conferencia = "Sim"

            rst.append(
                {
                    "Membro Matrícla": employee.matricula,
                    "Membro Nome": employee.pessoa_fisica.nome,
                    "Gratificação": record,
                    "Dias a Receber": calcular_dias_membro(
                        employee, payroll, record, pgto_servidor
                    ),
                    "Gratificação - Pgto": gratif_pgto,
                    "Gratificação - Origem Pgto": gratif_origem_pgto,
                    "Gratificação - Conferência": gratif_conferencia,
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)
