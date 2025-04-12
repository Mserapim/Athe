# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Q, ProtectedError
from django.db import transaction

from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger
from standard.models import Configuration, Choice
from rh.gfp.models import ContraCheque as Paycheck, Periodo
from rh.gfp.models import Evento as Event
from rh.gfp.models import FolhaEvento as Entry
from rh.gfp.models import FolhaModelo as ModelPayroll
from rh.gfp.models import (
    FolhaTipo,
    MarginConsignable,
    PaycheckDifference,
    PaycheckDifferenceItem,
    Periodo,
)
from rh.gfp.models import ConferenceEventPayroll
from rh.gfp.gcpp_utils import remove_gcpp_contracheque
from rh.models import PessoaFisica, Servidor as Employee
from standard.models import Configuration

from rh.gfp.folha_evento_hist_utils import criar_hist_contracheque

log = getLogger(__name__)
json = get_json_engine()


class GFPPayCheckReport(RestfulDRY):

    _model = Paycheck

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.PayCheckManage")')

    @login_required("JSON")
    def paycheck_list(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            employee = Employee.objects.get(pk=int(self.request.POST.get("employee")))
            month_start, year_start = self.request.POST["start"].split("/")

            if "start" in self.request.POST and self.request.POST["end"]:
                month_end, year_end = self.request.POST["end"].split("/")
                query_cc = Paycheck.objects.filter(servidor=employee).filter(
                    (
                        Q(
                            folha__periodo__mes__gte=month_start,
                            folha__periodo__ano=year_start,
                        )
                        | Q(folha__periodo__ano__gt=year_start)
                    )
                    & (
                        Q(
                            folha__periodo__mes__lte=month_end,
                            folha__periodo__ano=year_end,
                        )
                        | Q(folha__periodo__ano__lt=year_end)
                    )
                )
            else:
                query_cc = Paycheck.objects.filter(
                    servidor=employee,
                    folha__periodo__mes=month_start,
                    folha__periodo__ano=year_start,
                )

            log.debug(query_cc)

            if self.request.POST.get("type"):
                type_payroll = FolhaTipo.objects.get(
                    pk=int(self.request.POST.get("type"))
                )
                query_cc = query_cc.filter(folha__tipo_folha=type_payroll)

            list_paycheck = ",".join([str(cc.pk) for cc in query_cc])

            obj.update(list_paycheck=list_paycheck)
        except Exception as e:
            self.log.exception(e)
            obj["message"] = "Não foi possível obter as informações!"
            obj["success"] = False
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPPayCheck(RestfulDRY):

    _model = Paycheck

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__cpf__iexact",
    )

    force_persist_boolean_fields = [
        "automated",
    ]

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('rh.gfp.paycheck.PayCheckManage')")

    def get_icons(self, instance):
        """DOCSTRING."""
        icons = []

        from_to_employment_status = {
            "EM ATIVIDADE": "icon-fopag icon-user-active",
            "INATIVO": "icon-fopag icon-user-inactive",
            "PARTILHA": "icon-fopag icon-user-silhouette",
            "PENSÃO ALIMENTÍCIA": "icon-fopag icon-cookies",
        }
        icons.append(
            {
                "iconCls": from_to_employment_status.get(
                    instance.situacao_funcional, "icon-core icon-core-blank"
                ),
                "alt": instance.situacao_funcional,
            }
        )

        from_to_source_employee = {
            1: "icon-fopag icon-home",
            2: "icon-fopag icon-home-minus",
            3: "icon-fopag icon-home-plus",
            4: "icon-fopag icon-user-timer",
            5: "icon-fopag icon-notebook-minus",
        }
        icons.append(
            {
                "iconCls": from_to_source_employee.get(
                    instance.employee_source, "icon-core icon-core-blank"
                ),
                "alt": (
                    instance.get_employee_source_display()
                    if not instance.pensioner
                    else ""
                ),
            }
        )

        icons.append(
            {
                "iconCls": (
                    "icon-fopag icon-user-detective"
                    if instance.employee_pays_pension != 0 and not instance.pensioner
                    else "icon-core icon-core-blank"
                ),
                "alt": (
                    instance.get_employee_pays_pension_display()
                    if not instance.pensioner
                    else ""
                ),
            }
        )

        icons.append(
            {
                "iconCls": (
                    "icon-fopag icon-status-away"
                    if instance.alterado
                    else "icon-core icon-core-blank"
                ),
                "alt": "Falta consolidar informações" if instance.alterado else "",
            }
        )

        icons.append(
            {
                "iconCls": (
                    "icon-fopag icon-exclamation-black"
                    if instance.blocked
                    else "icon-core icon-core-blank"
                ),
                "alt": "Bloqueado" if instance.blocked else "",
            }
        )

        icons.append(
            {
                "iconCls": (
                    "icon-fopag icon-fopag icon-exclamation-circle"
                    if instance.validations
                    else "icon-core icon-core-blank"
                ),
                "alt": (
                    ["<p>%s</p>" % e for e in instance.validations]
                    if instance.validations
                    else ""
                ),
            }
        )

        return icons

    def model_to_dict(self, instance):
        """DOCSTRING."""
        _dict = super(GFPPayCheck, self).model_to_dict(instance)
        _dict.update(
            message=(
                instance.messages.get(entry=None).pk
                if instance.messages.filter(entry=None).exists()
                else None
            ),
            message_unicode=(
                instance.messages.get(entry=None).texto
                if instance.messages.filter(entry=None).exists()
                else ""
            ),
            icons=self.get_icons(instance),
            errors=instance.validations,
            cpf=instance.servidor.pessoa_fisica.cpf,
            previous_paycheck=instance.previous_paycheck,
            payroll_status=instance.folha.status,
        )

        return _dict

    @login_required("JSON")
    def select(self, args=[]):
        """DOCSTRING."""
        paycheck = Paycheck.objects.get(
            folha=self.request.POST.get("payroll"),
            servidor=self.request.POST.get("employee"),
        )
        obj = {"success": False}
        obj.update({"success": True, "paycheck": self.model_to_dict(paycheck)})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def apply_model(self, args=[]):
        """DOCSTRING."""
        obj = {"success": True}

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
            paycheck = self._model.objects.get(pk=self.request.POST.get("paycheck"))
            model = ModelPayroll.objects.get(slug=self.request.POST.get("model"))

            log.debug(">>>>>>>>>>>>>> APLICANDO MODELO PARA %s" % paycheck.servidor)
            try:
                paycheck.apply_model(model, self.request.user, force=True)
            except Exception as e:
                self.log.exception(e)
            else:
                self.log.debug(
                    ">>>>>>>>>>>> MODELO %s APLICADO EM %s" % (model, paycheck)
                )
            finally:
                pass

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def consolidate(self, args=[]):
        """DOCSTRING."""
        rst = {
            "success": False,
            "message": "ContraCheque não possui alterações para serem consolidadas!",
            "changed": False,
            "instance": None,
        }
        if "paycheck" in self.request.POST:
            paycheck = Paycheck.objects.get(pk=self.request.POST.get("paycheck"))
            log.debug("%s: %s" % (paycheck, self.request.POST))
            changes = paycheck.consolidate(changes=Paycheck.ALL, force=True, save=True)

            rst["success"] = True
            if changes:
                rst["message"] = "ContraCheque consolidado com sucesso!"
                rst["instance"] = self.model_to_dict(paycheck)
                rst["changed"] = True

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def calculate(self, args=[]):
        """DOCSTRING."""
        obj = {
            "lancamento": "F",
            "qnt": 0,
            "qnt_max": 0,
            "pct": 0.0,
            "parcela": 0.0,
            "installments_paid": 0.0,
            "prazo": 0.0,
            "valor_base": 0.0,
            "base_previdencia": 0.0,
            "patronal": 0.0,
            "valor": 0.0,
            "description": "",
            "reference_year": 0,
            "reference_month": 0,
            "memory": [],
        }

        paycheck = Paycheck.objects.get(pk=int(self.request.POST["paycheck"]))

        criar_hist_contracheque(paycheck)

        try:
            entry = (
                Entry.objects.get(pk=self.request.POST["entry"])
                if "entry" in self.request.POST and self.request.POST["entry"]
                else None
            )
            event = (
                entry.evento
                if entry
                else Event.objects.get(pk=self.request.POST["event"])
            )
            obj = {
                "qnt": round(entry.correct_qnt, 2) if entry else 0,
                "qnt_max": (
                    round(entry.correct_qnt_max or 0.00, 2)
                    if entry
                    else float(event.max_quantity)
                ),
                "pct": round(entry.correct_pct or 0, 6) if entry and entry.pct else 0,
                "parcela": entry.parcela if entry else 0.0,
                "prazo": entry.prazo if entry else 0.0,
                "valor_base": round(entry.correct_base_value, 2) if entry else 0.0,
                "base_previdencia": (
                    round(entry.correct_base_previdencia, 2) if entry else 0.0
                ),
                "patronal": round(entry.correct_patronal, 2) if entry else 0.0,
                "valor": round(entry.correct_valor, 2) if entry else 0.00,
                "reference_year": (
                    entry.reference_year if entry else paycheck.folha.periodo.ano
                ),
                "reference_month": (
                    entry.reference_month if entry else paycheck.folha.periodo.mes
                ),
                "info": entry.info if entry else "",
                "automated": entry.automated if entry else False,
            }

            if (entry and (entry.automated or entry.auto_calc_difference)) or (
                event.automated
                and event.calculation_at(paycheck.folha.date_range.first)
            ):
                classcode = (
                    entry.classcode
                    if entry
                    else event.calculation_at(paycheck.folha.date_range.first)
                )

                if classcode:
                    cls = classcode.cls
                    params = {}
                    if "qnt" in self.request.POST:
                        params["qnt"] = self.request.POST.get("qnt")
                    if "pct" in self.request.POST:
                        params["pct"] = self.request.POST.get("pct")
                    if "oIds" in self.request.POST:
                        params["oIds"] = self.request.POST.getlist("oIds")
                    params["info"] = self.request.POST.get("info")
                    cid = self.request.POST.get("cid", 0)
                    if cid == "":
                        cid = 0
                    params.update(entry.vars if entry else {})
                    calc = cls(
                        paycheck.servidor,
                        paycheck.folha,
                        event,
                        entry=entry,
                        pensioner=paycheck.pensioner,
                        cid=cid,
                        params=params,
                    )
                    log.debug("PARAMS: %s" % params)
                    ret = {}
                    try:
                        ret = calc.calculate()
                    except Exception as e:
                        log.exception(str(e))
                    finally:
                        obj["qnt"] = float(ret.get("qnt", 0.00))
                        obj["qnt_max"] = float(ret.get("qnt_max", obj["qnt_max"]))
                        obj["pct"] = float(ret.get("pct", 0.00))
                        obj["valor_base"] = float(ret.get("valor_base", 0.00))
                        obj["info"] = ret.get("info", "")
                        obj["validate"] = ret.get("validate", None)
                        obj["choices"] = ret.get("choices", [])
                        obj["oIds"] = ret.get("oIds", [])
                        if "cid" in ret:
                            obj["cid"] = ret.get("cid", "")
                        obj["automated"] = ret.get("automated", True)
                        obj["reference_year"], obj["reference_month"] = ret.get(
                            "references",
                            (paycheck.folha.periodo.ano, paycheck.folha.periodo.mes),
                        )
                        obj["correct_valor"] = float(ret.get("valor", 0))
                        obj["prazo"] = ret.get("prazo", 0)
                        obj["installments_paid"] = ret.get("installments_paid", 0)
                        obj["parcela"] = ret.get("parcela", 0)
                        obj["correct_base_previdencia"] = float(
                            ret.get("base_previdencia", 0)
                        )
                        obj["correct_patronal"] = float(ret.get("patronal", 0))
                        obj["valor"] = float(ret.get("valor", 0))
                        obj["patronal"] = float(ret.get("patronal", 0))
                        obj["base_previdencia"] = float(ret.get("base_previdencia", 0))
                        obj["memory"] = ret.get("memory", [])
                else:
                    self.log.error(f"Calculo não encontrado para {event}")

        except Exception as e:
            log.debug(obj)
            log.exception(e)
            obj["exception"] = "toolkit.exception.JSONError"
            obj["message"] = str(e)

        criar_hist_contracheque(paycheck)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def recalculate(self, args=[]):
        """DOCSTRING."""
        rst = {
            "success": False,
            "message": "Nada foi feito!",
            "changed": False,
            "instance": None,
        }

        if "paycheck" in self.request.POST:
            paycheck = Paycheck.objects.get(pk=self.request.POST.get("paycheck"))
            try:
                criar_hist_contracheque(paycheck)

                changes = paycheck.recalculate()
            except Exception as e:
                log.exception(str(e))
                rst["message"] = str(e)
            else:
                rst["success"] = True
                rst["message"] = (
                    "Recálculo realizado com sucesso!"
                    if changes.get("changed", False)
                    else "Nenhuma alteração!"
                )
                rst["changed"] = changes.get("changed", False)
                rst["instance"] = self.model_to_dict(paycheck)

                criar_hist_contracheque(paycheck)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def evaluate(self, args=[]):
        """DOCSTRING."""
        rst = {
            "success": False,
            "message": "Nada foi feito!",
            "changed": False,
            "instance": None,
        }

        if "paycheck" in self.request.POST:
            paycheck = Paycheck.objects.get(pk=self.request.POST.get("paycheck"))
            try:
                changes = paycheck.evaluate_differences()
            except Exception as e:
                log.exception(e)
                rst["message"] = str(e)
            else:
                rst["success"] = True
                rst["message"] = (
                    "Diferenças avaliadas com sucesso!"
                    if changes.get("changed", False)
                    else "Nenhuma alteração!"
                )
                rst["changed"] = changes.get("changed", False)
                rst["instance"] = self.model_to_dict(paycheck)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def confirm(self, args=[]):
        """PERMISSOES EXIGIDAS.

        can_validate_event_payroll: Validar eventos pendentes na folha de pagamento
        can_validate_event_internal_control: Validar eventos pendentes no controle interno.

        """
        rst = {"success": False, "message": "Nada foi feito ainda."}
        log.debug(self.request.POST)
        paycheck = Paycheck.objects.get(pk=self.request.POST.get("paycheck"))
        entries_pk = Entry.objects.filter(pk__in=self.request.POST.getlist("entries"))
        try:
            paycheck.confirm(entries_pk)
        except Exception as e:
            rst["message"] = str(e)
        else:
            rst["success"] = True
            rst["message"] = "Lançamentos confirmados com sucesso!"

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def vincular_pensionista(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        pensionista = PessoaFisica.objects.get(pk=self.request.POST.get("pk"))
        try:
            Entry.objects.filter(pk=self.request.POST.get("evento_id")).update(
                info=pensionista.abbreviation, cid=pensionista.pk
            )

        except Exception as e:
            rst["message"] = str(e)
        else:
            rst["success"] = True
            rst["message"] = "Vínculo realizado com sucesso!"

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def select_complement(self, args=[]):
        obj = {"success": False}
        complement = int(self.request.POST.get("complement"))

        log.debug("complement: %s" % complement)

        if complement is not None:
            cfg = Configuration.objects.get(application="gfp")
            cfg.set("complement", complement)
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def do_delete_single(self, pk):
        """Remove uma instância.

        :param pk: Chave primária de uma instância.
        :type pk: Integer
        """
        rst = {"success": False}

        try:
            inst = self.get_instance_model(pk)
        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado para remoção.")
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            try:
                remove_gcpp_contracheque(inst)
                inst.delete()
            except ProtectedError:
                rst.update(
                    message="Não posso remover os itens selecionados, pois, eles estão ligados a outros itens."
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update({"message": "Removido com sucesso!", "success": True})

        return rst

    def do_delete_multi(self):
        """Remove múltiplas instâncias."""
        rst = {"success": False}

        try:
            query = self.do_filter(self.get_query())
            rst.update(count=query.count())

            with transaction.atomic():
                for obj in query:
                    remove_gcpp_contracheque(obj)
                    obj.delete()
        except ProtectedError:
            rst.update(
                message="Não posso remover os itens selecionados, pois, eles estão ligados a outros itens."
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            rst.update({"success": True, "message": "Dados removidos com sucesso."})

        return rst


class GFPPayCheckNew(GFPPayCheck):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        cfg = Configuration.objects.get(application="gfp")
        period = cfg.get("periodo", "0")
        period = Periodo.objects.filter(pk=period)
        if period.exists():
            period = period.first()
            next_period = period.next
            if next_period:
                next_period = next_period.pk
            else:
                next_period = 0

            previous_period = period.previous
            if previous_period:
                previous_period = previous_period.pk
            else:
                previous_period = 0
            period = f"'period': {{'pk': {period.pk}, 'next_period': {next_period},  'previous_period': {previous_period}}}"
        else:
            period = "'period': {'pk': -1, 'next_period': '',  'previous_period': ''}"

        period = period.replace("None", "0")

        payroll_type = cfg.get("folhatipo", "0")
        payroll_type = f"'payrollType': '{payroll_type}'".replace("None", "0")
        complement = cfg.get("complement", "-1")
        complement = f"'complement': '{complement}'".replace("None", "-1")

        self.response["content-type"] = "text/javascript"
        self.response.write(
            f"Ext._create('rh.gfp.paycheck.PayCheckManageNew', {{{period}, {payroll_type}, {complement}}})"
        )


class GFPEntries(RestfulDRY):
    _model = Entry

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    page_size = 50

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "evento__numero__iexact",
        "evento__titulo__icontains",
    )

    def do_put(self, pk=None):
        """Executa uma requisição PUT.

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name
            )
        else:
            params = self.get_params(self.request.PUT, check_case=True)
            if "oIds" in params:
                params["oIds"] = [
                    int(params["oIds"]) if params["oIds"].isdigit() else params["oIds"]
                ]

            # Tipo de Inserção: 1 Automática ou 2 - Manual
            params["insertion_type"] = 1 if params["automated"] else 2

            paycheck = params.get("contracheque")

            criar_hist_contracheque(paycheck)

            if pk:
                params["id"] = pk
            fe, created_fe, of = paycheck.update_or_create_entry(**params)
            if created_fe or of:
                paycheck.recalculate()
                log.info(
                    "Contracheque criado: %s - %s" % (paycheck.servidor, paycheck.folha)
                )
            rst.update(
                {
                    "success": True,
                    "message": "Dados persistido com sucesso.",
                    "instance": self.model_to_dict(fe),
                }
            )

            criar_hist_contracheque(paycheck)

        return rst

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            params = self.get_params(self.request.POST, check_case=True)
            if "oIds" in params:
                params["oIds"] = [
                    int(params["oIds"]) if params["oIds"].isdigit() else params["oIds"]
                ]

            paycheck = params.get("contracheque")

            criar_hist_contracheque(paycheck)

            fe, created_fe, of = paycheck.update_or_create_entry(**params)
            if created_fe or of:
                paycheck.recalculate()
            rst.update(
                {
                    "success": True,
                    "message": "Dados persistido com sucesso.",
                    "instance": self.model_to_dict(fe),
                }
            )

            criar_hist_contracheque(paycheck)

        return rst

    def model_to_dict(self, instance):
        _dict = super(GFPEntries, self).model_to_dict(instance)
        payroll = instance.contracheque.folha
        _dict.update(
            icons=self.status_lancamento(instance),
            event_number=instance.evento.numero,
            event_type=instance.evento.tipo,
            prazo_desc=self.format_time(instance) if instance.prazo > 0 else "",
            reference="%02d/%04d - %s"
            % (payroll.periodo.mes, payroll.periodo.ano, payroll.tipo_folha),
            oIds=instance.get_cid_oids,
            message=instance.messages.get().pk if instance.messages.exists() else None,
            message_unicode=(
                str(instance.messages.get().texto) if instance.messages.exists() else ""
            ),
            full_description=f"{instance} ({instance.qnt:.0f}) - {instance.folha}",
        )

        return _dict

    def format_time(self, instance):
        now = date(
            day=1,
            month=(
                instance.folha.periodo.mes if instance.folha.periodo.mes <= 12 else 12
            ),
            year=instance.folha.periodo.ano,
        )
        months = instance.prazo - instance.parcela
        dt = now + relativedelta(months=(months if months > 0 else 0))
        return "%s de %s - %s" % (
            instance.parcela,
            instance.prazo,
            dt.strftime("%m/%Y"),
        )

    def status_lancamento(self, fe):
        entry_insertion_type = Choice.objects.get(
            app_label="gfp", name="ENTRY_INSERTION_TYPE", value=fe.insertion_type
        )

        title_automated = entry_insertion_type.label
        if (
            fe.automated and entry_insertion_type.value == 1
        ):  # se registro FolhaEvento tem o Tipo de Inserção 'automático'
            icon_automated = "icon-fopag icon-fopag icon-compile"
        elif (
            entry_insertion_type.value == 2
        ):  # se registro FolhaEvento tem o Tipo de Inserção 'manual'
            icon_automated = "icon-fopag icon-fopag icon-compile-warning"
        else:
            icon_automated = "icon-fopag icon-fopag icon-calendar-plus"

        obj = [
            {
                "iconCls": icon_automated,
                "title": title_automated,
                "alt": title_automated,
            },
            {
                "iconCls": (
                    "icon-fopag icon-calendar"
                    if fe.evento.lancamento == "F"
                    else "icon-fopag icon-timer"
                ),
                "title": "Fixo" if fe.evento.lancamento == "F" else "Temporário",
                "alt": "Fixo" if fe.evento.lancamento == "F" else "Temporário",
            },
        ]

        ptext = "<ul>"
        ptext += (
            ""
            if fe.confirma_folha is not None
            else "<li>Lançamento não foi confirmado pela Folha de Pagamento</li>"
        )
        ptext += (
            ""
            if fe.confirma_controle is not None
            else "<li>Lançamento não foi confirmado pelo Controle Interno</li>"
        )
        ptext += "</ul>"

        st = fe.confirma_folha is None or fe.confirma_controle is None
        if st is True:
            obj.append(
                {"iconCls": "icon-fopag icon-attention", "alt": ptext, "title": ptext}
            )
        else:
            obj.append(
                {
                    "iconCls": "icon-core icon-core-success",
                    "alt": "Lançamento confirmado!",
                    "title": "Lançamento confirmado!",
                }
            )

        if fe.paycheck_difference:
            obj.append(
                {
                    "iconCls": "icon-fopag icon-table-money",
                    "title": "Gerado por uma diferença",
                    "alt": "Gerado por uma diferença",
                }
            )
        else:
            obj.append({"iconCls": "icon-core icon-core-blank", "title": "", "alt": ""})

        if (
            fe.evento.evaluate_difference
            and fe.contracheque.folha.is_processed
            and fe.has_differences
        ):
            obj.append(
                {
                    "iconCls": "icon-fopag icon-task-select",
                    "title": "Diferenças em aberto",
                    "alt": "Diferenças em aberto",
                }
            )
        else:
            obj.append({"iconCls": "icon-core icon-core-blank", "title": "", "alt": ""})

        if fe.count_as_previous_exercise:
            obj.append(
                {
                    "iconCls": "icon-fopag icon-clock-select",
                    "title": "Contabilizado como exercício anterior",
                    "alt": "Contabilizado como exercício anterior",
                }
            )
        else:
            obj.append({"iconCls": "icon-core icon-core-blank", "title": "", "alt": ""})

        return obj


class GFPMarginConsignable(RestfulDRY):

    _model = MarginConsignable

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.paycheck.MarginConsignableManage")')

    def get_icons(self, instance):
        return [
            {
                "iconCls": (
                    "icon-fopag icon-status-busy"
                    if not instance.active
                    else "icon-fopag icon-status"
                ),
                "title": "INATIVO" if not instance.active else "ATIVO",
                "alt": "INATIVO" if not instance.active else "ATIVO",
            },
        ]

    def model_to_dict(self, instance):
        _dict = super(GFPMarginConsignable, self).model_to_dict(instance)
        _dict.update({"icons": self.get_icons(instance)})

        return _dict


class GFPEntryDifferenceShow(RestfulDRY):

    _model = Entry

    def model_to_dict(self, instance):
        params = super(GFPEntryDifferenceShow, self).model_to_dict(instance)
        payroll = instance.folha
        params.update(
            reference="%02d/%04d - %s"
            % (payroll.periodo.mes, payroll.periodo.ano, payroll.tipo_folha)
        )

        return params

    def get_query(self):

        if self.request.GET.get("entry"):
            diff = PaycheckDifferenceItem.objects.filter(
                entry_difference__pk=int(self.request.GET.get("entry"))
            ).values_list("difference__pk", flat=True)
            diff_pks = PaycheckDifference.objects.filter(pk__in=diff).values_list(
                "pk", flat=True
            )
            return Entry.objects.filter(paycheck_difference__in=diff_pks)

        return None


class GFPPayCheckConference(GFPPayCheck):

    _model = Paycheck

    def get_query(self):
        query = super(GFPPayCheck, self).get_query()
        diffs_current = (
            ConferenceEventPayroll.objects.filter(checked=False)
            .values_list("event_paycheck_current__pk", flat=True)
            .distinct()
        )
        # diffs_previous = ConferenceEventPayroll.objects.filter(checked=False).values_list(
        #     'event_paycheck_previous__pk', flat=True).distinct()
        # diffs = list(diffs_current)+list(diffs_previous)
        return query.filter(pk__in=diffs_current)

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.conference.payroll.Manage")')


class GFPConferenceEntries(GFPEntries):
    _model = Entry

    def set_status_conference(self, instance):
        conference = ConferenceEventPayroll.objects.filter(
            event_payroll_current=instance
        ).first()

        if conference:
            return conference.checked

        return False

    def set_status_conference_previuos(self, instance):
        conference = ConferenceEventPayroll.objects.filter(
            event_payroll_previous=instance
        ).first()

        if conference:
            return conference.checked

        return False

    def model_to_dict(self, instance):
        _dict = super(GFPEntries, self).model_to_dict(instance)
        payroll = instance.contracheque.folha
        _dict.update(
            icons=self.status_lancamento(instance),
            icons_previous=self.status_lancamento_previous(instance),
            event_number=instance.evento.numero,
            event_type=instance.evento.tipo,
            prazo_desc=self.format_time(instance) if instance.prazo > 0 else "",
            reference="%02d/%04d - %s"
            % (payroll.periodo.mes, payroll.periodo.ano, payroll.tipo_folha),
            oIds=instance.oIds,
            message=instance.messages.get().pk if instance.messages.exists() else None,
            message_unicode=(
                str(instance.messages.get().texto) if instance.messages.exists() else ""
            ),
            full_description=f"{instance} ({instance.qnt:.0f}) - {instance.folha}",
        )

        return _dict

    def status_lancamento(self, fe):
        entry_insertion_type = Choice.objects.get(
            app_label="gfp", name="ENTRY_INSERTION_TYPE", value=fe.insertion_type
        )

        title_automated = entry_insertion_type.label
        if (
            fe.automated and entry_insertion_type.value == 1
        ):  # se registro FolhaEvento tem o Tipo de Inserção 'automático'
            icon_automated = "icon-fopag icon-fopag icon-compile"
        elif (
            entry_insertion_type.value == 2
        ):  # se registro FolhaEvento tem o Tipo de Inserção 'manual'
            icon_automated = "icon-fopag icon-fopag icon-compile-warning"
        else:
            icon_automated = "icon-fopag icon-fopag icon-calendar-plus"

        obj = [
            {
                "iconCls": icon_automated,
                "title": title_automated,
                "alt": title_automated,
            },
            {
                "iconCls": (
                    "icon-fopag icon-calendar"
                    if fe.evento.lancamento == "F"
                    else "icon-fopag icon-timer"
                ),
                "title": "Fixo" if fe.evento.lancamento == "F" else "Temporário",
                "alt": "Fixo" if fe.evento.lancamento == "F" else "Temporário",
            },
        ]
        if self.set_status_conference(fe):
            obj.append(
                {
                    "iconCls": "icon-fopag  icon-exclamation-green",
                    "title": "Lançamento Ok",
                    "alt": "Status do lançamento",
                }
            )
        else:
            obj.append(
                {
                    "iconCls": "icon-fopag icon-exclamation-red",
                    "title": "Lançamento Diferente",
                    "alt": "Status do lançamento",
                }
            )

        return obj

    def status_lancamento_previous(self, fe):
        entry_insertion_type = Choice.objects.get(
            app_label="gfp", name="ENTRY_INSERTION_TYPE", value=fe.insertion_type
        )

        title_automated = entry_insertion_type.label
        if (
            fe.automated and entry_insertion_type.value == 1
        ):  # se registro FolhaEvento tem o Tipo de Inserção 'automático'
            icon_automated = "icon-fopag icon-fopag icon-compile"
        elif (
            entry_insertion_type.value == 2
        ):  # se registro FolhaEvento tem o Tipo de Inserção 'manual'
            icon_automated = "icon-fopag icon-fopag icon-compile-warning"
        else:
            icon_automated = "icon-fopag icon-fopag icon-calendar-plus"

        obj = [
            {
                "iconCls": icon_automated,
                "title": title_automated,
                "alt": title_automated,
            },
            {
                "iconCls": (
                    "icon-fopag icon-calendar"
                    if fe.evento.lancamento == "F"
                    else "icon-fopag icon-timer"
                ),
                "title": "Fixo" if fe.evento.lancamento == "F" else "Temporário",
                "alt": "Fixo" if fe.evento.lancamento == "F" else "Temporário",
            },
        ]

        if self.set_status_conference_previuos(fe):
            obj.append(
                {
                    "iconCls": "icon-fopag  icon-exclamation-green",
                    "title": "Lançamento Ok",
                    "alt": "Status do lançamento",
                }
            )
        else:
            obj.append(
                {
                    "iconCls": "icon-fopag icon-exclamation-red",
                    "title": "Lançamento Diferente",
                    "alt": "Status do lançamento",
                }
            )

        return obj

    @login_required("JSON")
    def checked(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}
        try:
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para alterar %s."
                    % self.Model._meta.object_name
                )
            else:
                entries_conference = ConferenceEventPayroll.objects.filter(
                    Q(conference__payroll=self.request.POST.get("payroll")),
                    Q(
                        event_payroll_current__pk__in=self.request.POST.getlist(
                            "entries"
                        )
                    )
                    | Q(
                        event_payroll_previous__pk__in=self.request.POST.getlist(
                            "entries"
                        )
                    ),
                ).distinct()
                for conference in entries_conference:
                    conference.checked = True
                    conference.save()
                rst["success"] = True
                rst["message"] = "Lançamentos conferidos com sucesso!"

        except Exception as e:
            rst["message"] = str(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.conference.payroll.EntriesManage")')
