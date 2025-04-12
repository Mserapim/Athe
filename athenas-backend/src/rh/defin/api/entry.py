import json

from decimal import Decimal
from datetime import datetime, date
from calendar import monthrange
from django.core.exceptions import ValidationError

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.decorator import login_required
from engine.mq.models import Task

from rh.defin.models import PFProviderEntry
from rh.gfp.models import Evento, Folha, FolhaEvento
from rh.gfp.paycheckdifference_utils import calc_from_period
from rh.defin.tasks_eventualprovider import applicate_eventual_provider_task

from rh.gfp.models import IRRF

log = getLogger(__name__)


class DEFINPFProviderEntryRestful(RestfulDRY):

    _model = PFProviderEntry

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.defin.entry.pf_provider.Manage")')

    def model_to_dict(self, instance):
        params = super(DEFINPFProviderEntryRestful, self).model_to_dict(instance)

        params.update(
            {
                "icon_applied_payroll": self.get_icon(instance),
            }
        )
        return params

    @login_required("JSON")
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
            try:
                deducao_benefica = (
                    IRRF.objects.order_by("-data_vigencia").first().deducao_benefica
                )

                params = self.get_params(self.request.POST, check_case=True)
                inst = self.factoryModel(**params)

                if not inst.gross_value:
                    raise Exception("Favor preencher o Valor Bruto")

                employee = inst.natural_person.servidor_set.filter(
                    type_by_possession="COE"
                ).first()
                periodo_filtro = datetime.now().date()
                payroll = Folha.objects.get(
                    periodo__mes=periodo_filtro.month,
                    periodo__ano=periodo_filtro.year,
                    tipo_folha__titulo="NORMAL",
                )

                gross_value = float(inst.gross_value)
                valor_base = 0

                inss_value = self.calculate_inss(inst, employee, payroll, gross_value)

                if inst.inss_exempt:
                    valor_base = gross_value - float(deducao_benefica)
                    liquid_value = gross_value
                else:
                    liquid_value = gross_value - inss_value
                    valor_base = liquid_value

                irrf_value = self.calculate_irrf(inst, employee, payroll, valor_base)

                liquid_value -= irrf_value

                inst.inss_value = round(Decimal(inss_value), 2)
                inst.ir_value = round(Decimal(irrf_value), 2)
                inst.liquid_value = round(Decimal(liquid_value), 2)

                if self.use_full_clean:
                    inst.full_clean()

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
                try:
                    errors = [
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ]
                    rst.update(message=str(errors[0]["values"][0]))
                except:
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
    def do_put_single(self, pk=None):
        """Atualiza uma instância."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            log.debug(
                "COUNT UPDATE FOR %s [%s,]: %s"
                % (self.Model.__name__, pk, self.Model.objects.filter(pk=pk).count())
            )
            params = self.get_params(self.request.PUT, check_case=True)
            log.debug("PUT GETPARAMS....")
            log.debug(json.dumps(params, default=str))
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

                deducao_benefica = (
                    IRRF.objects.order_by("-data_vigencia").first().deducao_benefica
                )

                employee = inst.natural_person.servidor_set.filter(
                    type_by_possession="COE"
                ).first()
                periodo_filtro = datetime.now().date()
                payroll = Folha.objects.get(
                    periodo__mes=periodo_filtro.month,
                    periodo__ano=periodo_filtro.year,
                    tipo_folha__titulo="NORMAL",
                )

                gross_value = float(inst.gross_value)
                valor_base = 0

                inss_value = self.calculate_inss(inst, employee, payroll, gross_value)

                if inst.inss_exempt:
                    valor_base = gross_value - float(deducao_benefica)
                    liquid_value = gross_value
                else:
                    liquid_value = gross_value - inss_value
                    valor_base = liquid_value

                irrf_value = self.calculate_irrf(inst, employee, payroll, valor_base)

                liquid_value -= irrf_value

                inst.inss_value = round(Decimal(inss_value), 2)
                inst.ir_value = round(Decimal(irrf_value), 2)
                inst.liquid_value = round(Decimal(liquid_value), 2)

                if self.use_full_clean:
                    inst.full_clean()

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
    def calculate_inss(self, inst, employee, payroll, base_value):
        if inst.inss_exempt:
            inss_value = 0
        else:
            event = Evento.objects.get(numero="89900")
            params = {"base_value": base_value}
            res = calc_from_period(employee, payroll, event, params)
            inss_value = res["valor"]
        return inss_value

    @login_required("JSON")
    def calculate_irrf(self, inst, employee, payroll, base_value):
        event = Evento.objects.get(numero="99700")
        params = {"base_value": base_value}
        res = calc_from_period(employee, payroll, event, params)
        return res["valor"]

    @login_required("JSON")
    def import_eventual_provider(self, payroll):
        rst = {"success": True, "message": ""}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst["success"] = False
            rst["message"] = f"Você não tem permissão para realizar a importação."
        else:
            payroll = Folha.objects.get(pk=int(self.request.POST.get("payroll")))
            if payroll.tipo_folha.modelo.titulo != "PRESTADORES DE SERVIÇO":
                rst["success"] = False
                rst["message"] = (
                    f"Selecione o Tipo de Folha correspondente à importação que deseja realizar."
                )
            elif payroll.is_closed:
                rst["success"] = False
                rst["message"] = f"Não é permitido importar para Folha fechada."
            else:
                dt_inicio = date(
                    day=1, month=payroll.periodo.mes, year=payroll.periodo.ano
                )
                dt_fim = dt_inicio.replace(
                    day=monthrange(dt_inicio.year, dt_inicio.month)[1]
                )
                entries = PFProviderEntry.objects.filter(
                    pay_day__gte=dt_inicio, pay_day__lte=dt_fim, applied_payroll=False
                ).distinct("natural_person")

                evento = Evento.objects.get(numero="60000")
                for entry in entries:
                    employee = entry.natural_person.servidor_set.filter(
                        type_by_possession="COE"
                    ).first()
                    payroll_entry = FolhaEvento.objects.filter(
                        evento=evento,
                        servidor=employee,
                        reference_year=entry.pay_day.year,
                        reference_month=entry.pay_day.month,
                    )
                    if not payroll_entry:
                        Task.start(
                            applicate_eventual_provider_task,
                            description=f"Aplicando lançamento de Prestador Eventual: {entry}",
                            user=self.request.user.id,
                            entry_id=entry.pk,
                            payroll_id=payroll.pk,
                        )

                        rst["message"] = (
                            f"Iniciando aplicação de lançamento de Prestador Eventual: {entry}."
                        )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(rst))

    def get_icon(self, instance):
        obj = [
            {
                "iconCls": (
                    "icon-fopag icon-money-plus"
                    if instance.applied_payroll
                    else "icon-fopag icon-money-exclamation"
                ),
                "title": (
                    "Lançamento Incluso na Folha"
                    if instance.applied_payroll
                    else "Lançamento Não Incluso na Folha"
                ),
                "alt": (
                    "Lançamento Incluso na Folha"
                    if instance.applied_payroll
                    else "Lançamento Não Incluso na Folha"
                ),
            },
        ]

        return obj
