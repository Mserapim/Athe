# -*- coding: utf-8 -*-

from datetime import datetime
from django.db.models import Q

from rh.ponto.models import Falta
from standard.models import RunCodeManager, Item
from rh.gfp.models import ExtraPaymentPeriod

from rh.gfp.calcs.mpmt.base import BaseCalculation, WorkDaysCalculation
from rh.gfp.calcs.mpmt.aid import AidSupply

from contrib.decorator import cache_return
from contrib.utils import getLogger

DIASCOMERCIAL = 30

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpmt-fault")
class Fault(BaseCalculation):

    title = "Cálculo de faltas"

    FULL_VALUE = True

    def valid_day(self, fault):
        return True

    @cache_return
    def quantity(self):
        return self.get_faults()

    def get_faults(self):
        faults = Falta.objects.filter(
            servidor=self.employee,
            injustificada__gt=0,
            data__range=(self.payroll.date_range.first, self.payroll.date_range.last),
        )
        fault_days = 0
        for f in faults:
            if self.valid_day(f):
                fault_days += f.injustificada / 60 / (f.carga_horaria.quantidade / 5)

        return round(fault_days, 3)

    def maximum_quantity(self):
        return self.payroll.date_range.days


class BaseHours(BaseCalculation):

    title = "Cálculo de Horas Negativas"

    FULL_VALUE = True

    RECALCULATE_BASES = 3

    def base_value(self):
        base = super(BaseHours, self).base_value()
        base = min(base, self.base_ceiling)
        return base

    @cache_return
    def quantity(self):
        return self.get_faults()

    @cache_return
    def maximum_quantity(self):
        return 154.00

    @property
    def base_ceiling(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )


@RunCodeManager.register("gfp-mpmt-negative-hours")
class NegativeHours(BaseHours):

    def get_faults(self):
        faltas = Falta.objects.filter(
            servidor=self.employee,
            horas_negativas__gt=0,
            data__range=(self.payroll.date_range.first, self.payroll.date_range.last),
        )
        fault_days = 0
        for f in faltas:
            fault_days += f.horas_negativas / 60

        return round(fault_days, 2)

    def full_value(self):
        return self.value()  # / self.factor_quantity()


@RunCodeManager.register("gfp-mpmt-positive-hours")
class PositiveHours(BaseHours):

    def get_faults(self):
        faltas = Falta.objects.filter(
            servidor=self.employee,
            horas_positivas__gt=0,
            data__range=(self.payroll.date_range.first, self.payroll.date_range.last),
        )
        fault_days = 0
        for f in faltas:
            fault_days += f.horas_positivas / 60

        return round(fault_days, 2)

    def percentage(self):
        return 150.00


@RunCodeManager.register("gfp-mpmt-fault-aid-supply")
class AidSupplyFault(AidSupply, Fault):

    def valid_day(self, fault):
        return fault.data.weekday() not in [5, 6]

    @cache_return
    def quantity(self):
        work_days_of_month = self.range_salary.work_days
        worked_days_of_month = self.range_salary_for().work_days
        faults = self.get_faults()
        qtd_max = self.maximum_quantity()

        if worked_days_of_month == 0:
            return worked_days_of_month

        if work_days_of_month == faults:
            faults = qtd_max

        if worked_days_of_month > qtd_max:
            faults = float(faults) - float(worked_days_of_month - qtd_max)

        log.debug(
            f"AidSupplyFault F:{faults} WDM:{work_days_of_month} {faults == work_days_of_month} WEDM:{worked_days_of_month} QM:{qtd_max}"
        )

        return faults if faults < qtd_max else qtd_max


@RunCodeManager.register("gfp-mpmt-faltasubsidio")
class FaltaSubsidio(WorkDaysCalculation):
    title = "Cálculo Base para desconto de Falta(s) de Efetivo/Comissionado no Subsídio"

    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)

        return 0.00

    def qnt_subsidio(self):
        return (
            self.range_salary_for().business_days
            if self.BASE_BUSINESSDAYS
            else self.range_salary_for().days
        )

    def value(self):
        value = (
            (self.base_value() / self.qnt_subsidio()) * self.quantity()
            if self.quantity() > 0
            else 0
        )

        return value

    def validar_efe_cms(self):
        if (
            self.employee.type_by_possession != "EFE"
            and self.employee.type_by_possession != "CMS"
        ):
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada a Efetivos ou Comissionados!"
            )

    def validate(self):
        self.validar_efe_cms()


@RunCodeManager.register("gfp-mpmt-faltaalimentacao")
class FaltaAlimentacao(WorkDaysCalculation):
    title = "Cálculo Base para desconto de Falta(s) de Efetivo/Comissionado no Auxílio Alimentação"

    def buscar_contracheque(self):
        q_cc = self.payroll.paychecks.filter(servidor=self.employee)

        return q_cc.first() if q_cc.exists() else None

    def buscar_fe_aux_alimentacao(self, cc):
        q_fe = cc.lancamentos.filter(evento__numero="06700")  # Auxílio Alimentação

        return q_fe.first() if q_fe.exists() else None

    def buscar_config_vigente(self):
        hoje = datetime.now()
        q_config = ExtraPaymentPeriod.objects.filter(
            extra_payment=2,
            employee__isnull=True,
            start_validity__lte=hoje,
        ).filter(Q(end_validity__isnull=True) | Q(end_validity__gte=hoje))

        return (
            q_config.order_by("-start_validity").first() if q_config.exists() else None
        )

    def base_value(self):
        q_config_event = self.buscar_config_vigente()

        if q_config_event is None:
            return 0.00
        else:
            return float(q_config_event.value)

    def maximum_quantity(self):
        cc = self.buscar_contracheque()
        fe_aux_alimentacao = self.buscar_fe_aux_alimentacao(cc)

        return float(fe_aux_alimentacao.qnt)

    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)

        return 0.00

    def value(self):
        value = (self.base_value() / self.maximum_quantity()) * self.quantity()

        return value

    def validar_efe_cms(self):
        if (
            self.employee.type_by_possession != "EFE"
            and self.employee.type_by_possession != "CMS"
        ):
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada a Efetivos ou Comissionados!"
            )

    def validate(self):
        self.validar_efe_cms()


@RunCodeManager.register("gfp-mpmt-faltagratificacao")
class FaltaGratificacao(WorkDaysCalculation):
    title = "Cálculo Base para desconto de Falta(s) de Efetivo/Comissionado no Auxílio Alimentação"

    def buscar_contracheque(self):
        q_cc = self.payroll.paychecks.filter(servidor=self.employee)

        return q_cc.first() if q_cc.exists() else None

    def buscar_fe_gratificacao(self, cc, chave):
        evento = Item.objects.get(key=chave).value
        q_fe = cc.lancamentos.filter(evento__numero=evento)

        return q_fe.first() if q_fe.exists() else None

    def base_value(self):
        cc = self.buscar_contracheque()
        q_dili = self.buscar_fe_gratificacao(cc, "evento_grat_diligencia")
        q_aux_coord = self.buscar_fe_gratificacao(cc, "evento_grat_aux_coord")

        if q_dili is None and q_aux_coord is None:
            return 0.00
        else:
            return float(q_dili.value if q_dili else 0.00) + float(
                q_aux_coord.value if q_aux_coord else 0.00
            )

    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)

        return 0.00

    def value(self):
        log.info(f"self.base_value(): {self.base_value()}")
        log.info(f"self.maximum_quantity(): {self.maximum_quantity()}")
        log.info(f"self.quantity(): {self.quantity()}")
        value = (self.base_value() / self.maximum_quantity()) * self.quantity()

        return value

    def validar_efe_cms(self):
        if (
            self.employee.type_by_possession != "EFE"
            and self.employee.type_by_possession != "CMS"
        ):
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada a Efetivos ou Comissionados!"
            )

    def validate(self):
        self.validar_efe_cms()
