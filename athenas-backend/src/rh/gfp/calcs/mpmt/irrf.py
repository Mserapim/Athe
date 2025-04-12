# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from django.db.models import Max, Q, Sum

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpmt.base import BaseCalculation
from rh.gfp.models import IRRF as IRRFModel
from rh.gfp.models import RRA, IRRFFaixa, RRAServidorFolhaTipo
from rh.models import Dependencia, ProcessSuspension
from standard.models import RunCodeManager, Choice

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpmt-irrf")
class IRRF(BaseCalculation):
    title = "Calculo de imposto retido na fonte"

    ALL_PAYROLL = True
    RECALCULATE_BASES = 2
    PARAMS_ = ["info", "oIds", "base_value"]

    def __init__(self, employee, payroll, event=None, entry=None, cid=None, **kwargs):
        """
        Inicializador do calculo, recebe o servidor, folha a ser calculada e o evento que possui o calculo automático.
        """
        super(IRRF, self).__init__(employee, payroll, event, entry, cid=cid, **kwargs)
        if self.suspension:
            self.exclude_events += [
                ev.numero for ev in self.suspension.process.gfp_events.all()
            ]
            log.debug("CHANGING EXCLUDED EVENTS TO %s" % self.exclude_events)

    @property
    def suspension(self):
        return ProcessSuspension.objects.filter(
            (Q(process__all_employees=True) | Q(process__employees=self.employee))
            & Q(
                process__matter_process=1,  # Tributária
                indicative_suspension=90,  # Decisão Definitiva a favor do contribuinte
                scope_decision=1,  # IRRF
                start_validity__lte=self.range_salary.first,
            )
        ).first()

    @cache_return
    def irrf(self):
        return IRRFModel.objects.exclude(
            data_vigencia__gt=self.range_salary.first
        ).order_by("-data_vigencia")[0]

    def molestia_grave_no_periodo(self):
        if (
            self.employee.molestia
            and self.employee.molestia.data_laudo < self.range_salary.last
        ):
            return True
        return False

    @cache_return
    def range(self):
        irrf = self.irrf()
        base_value = self.base_value()
        obj = {"percentage": 0.0, "discount": 0.0}

        for irrf_range in irrf.faixas.all():
            if base_value >= float(irrf_range.limite_inferior) and base_value <= float(
                irrf_range.limite_superior
            ):
                obj["percentage"] = float(irrf_range.percentual)
                obj["discount"] = float(irrf_range.desconto)
                break

        self._memory.append(
            f'FAIXA = {obj["percentage"]}% DEDUTOR = R$ {obj["discount"]}'
        )

        return obj

    @property
    def _dependents(self):
        deps = Dependencia.objects.filter(
            Q(
                tipo=1,
                suspenso=False,
                data_inicio__lte=self.range_salary.last,
                dependente__responsavel=self.employee.pessoa_fisica,
            )
            & (Q(data_fim=None) | Q(data_fim__gte=self.range_salary.last))
        )
        return deps

    @cache_return
    def quantity(self):
        return self._dependents.values("dependente__pessoa_fisica").distinct().count()

    def discounts(self):
        total = 0
        if self.ALL_PAYROLL and self.reference_payroll.tipo_folha.principal:
            query = self.employee.lancamentos.filter(
                contracheque__folha__periodo=self.reference_payroll.periodo,
                contracheque__event=self.event,
                contracheque__pensioner=self.pensioner,
            )
            # if self.payroll.periodo.mes != 13:
            #     query = query.exclude(contracheque__folha__tipo_folha__numero__in = (2,9))
            if self.entry:
                query = query.exclude(pk=self.entry.pk)
            for fe in query:
                total += fe.correct_value

        log.debug("DISCOUNTS: %s" % total)

        return float(total)

    @cache_return
    def discount_dependent(self):
        irrf = self.irrf()
        vl = float(irrf.valor_dependente)
        return self.quantity() * vl

    @cache_return
    def discount_sixty_five_years_inactive(self):
        value_discount = 0
        if self.employee.type_by_possession in ("SAP", "MAP", "MAP2", "BFP", "APO"):
            dt_payroll = self.range_salary.last
            dt_niver = self.employee.pessoa_fisica.data_nascimento
            years = relativedelta(dt_payroll, dt_niver).years
            if years >= 65:
                irrf = self.irrf()

                if irrf.valor_isencao_65_anos is None:
                    init_range = irrf.faixas.order_by("limite_inferior").first()
                    value_discount = float(init_range.limite_superior)
                else:
                    value_discount = float(irrf.valor_isencao_65_anos)

        return value_discount

    def base_discounts(self):
        discount_dep = self.discount_dependent()
        discount_65 = self.discount_sixty_five_years_inactive()
        self._memory.append(f"DESCONTO DEPENDENTE = {discount_dep}")
        self._memory.append(f"DESCONTO > 65 anos = {discount_65}")
        return discount_dep + discount_65

    def percentage(self):
        irrf_range = self.range()
        return irrf_range["percentage"]

    @cache_return
    def value(self):
        if (
            self.employee.molestia
            and self.employee.molestia.data_laudo < self.range_salary.last
        ):
            self._memory.append(
                "VALOR BASE = R$ 0,00 (Servidor possui moléstia grave cadastrada)"
            )
            return 0.00
        base_value = self.base_value()
        percentage = self.percentage()
        base_1 = base_value * percentage / 100.0
        self._memory.append(
            f"VALOR BASE 2 = {base_value}(VALOR BASE) * {percentage}(FAIXA) / 100 = {base_1}"
        )
        value = base_1 - self.range().get("discount", 0.00)
        self._memory.append(
            f'VALOR = {base_1}(VALOR BASE 2) - {self.range().get("discount", 0.00)}(DESCONTOS) = {value}'
        )
        cut_off_value = self.get_cut_off_value()
        if cut_off_value and value < float(cut_off_value.first().label):
            value = 0
        return value

    def get_cut_off_value(self):
        return Choice.objects.filter(
            name="CUT_OFF_VALUE_FOR_IRRF", app_label="defin"
        ).order_by("-value")


@RunCodeManager.register("gfp-mpmt-irrf-rra")
class IRRFRRA(IRRF):
    titulo = "Calculo de imposto retido na fonte com RRA"

    MULTI_CALCULATE = True

    @property
    def pensions(self):
        query = self.employee.pensao_pagador.exclude(
            Q(data_inicio__gt=self.range_salary.last)
            | (~Q(data_fim=None) & Q(data_fim__lt=self.range_salary.first))
        ).filter(type_of_pension=2)
        return query

    def validate(self):
        if self.pensioner is None and self.pensions.exists():
            raise self.CalculationNotApplicable(
                "Cálculo não aplicado a quem tem pensão por morte!"
            )

    def base_value_query(self):
        query = super(IRRFRRA, self).base_value_query()
        if self.object:
            return query.filter(rra_employee__rra=self.object)
        return query

    def _get_query(self):
        if self.params.get("oIds"):
            return RRA.objects.filter(pk__in=self.params.get("oIds"))
        entries = (
            super(IRRFRRA, self)
            .base_value_query()
            .order_by("rra_employee__rra_id")
            .values("rra_employee__rra")
            .distinct()
        )
        return RRA.objects.filter(pk__in=[r["rra_employee__rra"] for r in entries])

    @cache_return
    def event_information(self):
        if self.object:
            return "%s" % self.object
        return ""

    @cache_return
    def quantity(self):
        return 0

    def discount_dependent(self):
        return 0.0

    @property
    def rra_factor(self):
        if self.object:
            installments = (
                self.base_value_query().aggregate(total=Max("prazo")).get("total") or 1
            )
            installments_paid = (
                self.base_value_query()
                .aggregate(total=Max("installments_paid"))
                .get("total")
                or 1
            )
            if installments > 0:
                months = self.object.employeers.get(employee=self.employee).months
                return (float(months) / float(installments)) * float(installments_paid)
        return 0

    def range(self):
        try:
            irrf = self.irrf()
            rra_quantity = float(self.rra_factor)
        except RRAServidorFolhaTipo.DoesNotExist:
            rra_quantity = 1.00
        except Exception as e:
            self.log.exception(e)

        normatized_base_value = self.base_value() / rra_quantity
        obj = {"percentage": 0, "discount": 0}

        try:
            range_ = irrf.faixas.get(
                limite_inferior__lte=normatized_base_value,
                limite_superior__gte=normatized_base_value,
            )
        except IRRFFaixa.DoesNotExist:
            log.info(
                "Base IRRF: %s. Utilizando a faixa isenta do IRRF!"
                % normatized_base_value
            )
        except Exception as e:
            log.exception(e)
        else:
            obj["percentage"] = float(range_.percentual)
            obj["discount"] = float(range_.desconto) * rra_quantity

        # log.debug('IRRF %s: RRA %s: BV %s: NBV %s: RP %s: RD %s: NRD %s' % (irrf, rra_quantity, self.base_value(
        # ), normatized_base_value, range_.percentual, range_.desconto, obj["discount"]))

        return obj


@RunCodeManager.register("gfp-mpmt-irrf-eventual-provider")
class IRRFEventualProvider(IRRF):

    title = "Cálculo de imposto retido na fonte para prestadores de serviço eventuais"

    def validate_eventual_provider(self):
        if self.employee.type_by_possession != "COE":
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada para Prestadores de Serviços Eventuais"
            )

    def validate(self):
        self.validate_eventual_provider()


@RunCodeManager.register("gfp-mpmt-irrf-susp")
class IRRFSuspension(IRRF):
    title = "Calculo de imposto não retido na fonte "

    CALCULATE_OVER = 2
    RRA_CALC = False

    MEMORY_DISCOUNT_DESC = "DESCONTO DEPENDENTES"
    SHOW_MEMORY = True

    RECALCULATE_BASES = 2

    def __init__(self, employee, payroll, event=None, entry=None, cid=None, **kwargs):
        """
        Inicializador do calculo, recebe o servidor, folha a ser calculada e o evento que possui o calculo automático.
        """
        super(IRRFSuspension, self).__init__(
            employee, payroll, event, entry, cid=cid, **kwargs
        )
        self.exclude_events = []

    def configure(self): ...

    def validate(self):
        self.validate_not_paycheck_pension()
        # log.debug('VALIDATE PENSION...')
        # log.debug(self.base_value_query())
        if not self.suspension:
            raise self.CalculationNotApplicable(
                "Cálculo apenas para quem tem processo de suspensão tributária (IRRF)!"
            )

    def discount_paid_other_payroll(self, value_field="valor"):
        # TODO Verificar se é necessário utilizar o valor realmente pago no lugar
        # do correct_valor
        entries = self.employee.entries.filter(
            evento__in=self.event.relationships,
            status="CT",
            contracheque__pensioner=self.pensioner,
            contracheque__folha__periodo=self.reference_payroll.periodo,
        )
        if self.entry:
            entries = entries.exclude(pk=self.entry.pk)
        value = float(entries.aggregate(total=Sum(value_field)).get("total") or 0)
        # log.debug(value)
        return value

    def total_value_suspended(self):
        only_events = self.only_events
        self.only_events = [
            ev.numero for ev in self.suspension.process.gfp_events.all()
        ]
        query = self.base_value_query()
        total = query.aggregate(total=Sum("value")).get("total") or 0
        self.only_events = only_events
        return float(total)

    def vars(self):
        """
        Informações para eSocial (S-1210).
            tpProcRet: Tipo de processo de não retenção (1 - Administrativo, 2 - Judicial)
            nrProcRet: Número do processo de não retenção (S-1070)
            codSusp: Código da suspensão (pk da suspensão do processo de retenção)
            vlrRendSusp: Valor da renda suspensa de tributação
        """
        _vars = super().vars()
        _vars["tpProcRet"] = self.suspension.process.type_process
        _vars["nrProcRet"] = self.suspension.process.number_process
        _vars["codSusp"] = self.suspension.pk
        # FIXME: O valor precisa ser a diferença entre o valor do IRRF sem suspensão e com suspensão
        _vars["vlrRendSusp"] = round(self.total_value_suspended(), 2)
        return _vars


@RunCodeManager.register("gfp-mpmt-irrf-info65")
class IRRFInfo65(IRRF):
    title = "Calculo de imposto não retido na fonte para maior ou igual a 65 anos"

    CALCULATE_OVER = 2
    SHOW_MEMORY = True

    RECALCULATE_BASES = 2

    def validate(self):
        if (
            self.molestia_grave_no_periodo()
            or not self.discount_sixty_five_years_inactive() > 0
        ):
            raise self.CalculationNotApplicable(
                "Cálculo aplicado apenas para quem tem idade maior ou igual que 65 anos e não tem moléstia grave!"
            )

    def base_discounts(self):
        discount_dep = self.discount_dependent()
        self._memory.append(f"DESCONTO DEPENDENTE = {discount_dep}")
        return discount_dep

    def calc_base_value(self, base_value):
        percentage = self.percentage()
        base_1 = base_value * percentage / 100.0
        self._memory.append(
            f"VALOR BASE 2 = {base_value}(VALOR BASE) * {percentage}(FAIXA) / 100 = {base_1}"
        )
        value = base_1 - self.range().get("discount", 0.00)
        self._memory.append(
            f'VALOR = {base_1}(VALOR BASE 2) - {self.range().get("discount", 0.00)}(DESCONTOS) = {value}'
        )
        cut_off_value = self.get_cut_off_value()
        if cut_off_value and value < float(cut_off_value.first().label):
            value = 0
        return value

    @cache_return
    def value(self):
        base_value_65 = self.base_value() - self.discount_sixty_five_years_inactive()
        base_value = self.base_value()
        value = self.calc_base_value(base_value)
        value_65 = self.calc_base_value(base_value_65)
        return value - value_65


@RunCodeManager.register("gfp-mpmt-irrf-info-molestia")
class IRRFInfoMolestia(IRRF):
    title = "Calculo de imposto não retido na fonte para quem tem moléstia grave"

    CALCULATE_OVER = 2
    SHOW_MEMORY = True

    RECALCULATE_BASES = 2

    def validate(self):
        if not self.molestia_grave_no_periodo():
            raise self.CalculationNotApplicable(
                "Cálculo aplicado apenas para quem tem moléstia grave!"
            )

    @cache_return
    def value(self):
        base_value = self.base_value()
        percentage = self.percentage()
        base_1 = base_value * percentage / 100.0
        self._memory.append(
            f"VALOR BASE 2 = {base_value}(VALOR BASE) * {percentage}(FAIXA) / 100 = {base_1}"
        )
        value = base_1 - self.range().get("discount", 0.00)
        self._memory.append(
            f'VALOR = {base_1}(VALOR BASE 2) - {self.range().get("discount", 0.00)}(DESCONTOS) = {value}'
        )
        cut_off_value = self.get_cut_off_value()
        if cut_off_value and value < float(cut_off_value.first().label):
            value = 0
        return value
