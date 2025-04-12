# -*- coding: utf-8 -*-

from django.db import models

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import BaseCalculation
from rh.gfp.models import ExtraPaymentPeriod
from rh.ponto.models import Falta
from standard.models import RunCodeManager

from rh.gfp.calcs.mpto.aid import AidSupply

DIASCOMERCIAL = 30

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpto-fault")
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

    FORCE_RECALCULATE_BASE = True

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


@RunCodeManager.register("gfp-mpto-negative-hours")
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


@RunCodeManager.register("gfp-mpto-positive-hours")
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


@RunCodeManager.register("gfp-mpto-fault-aid-supply")
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

        # log.debug(f'AidSupplyFault F:{faults} WDM:{work_days_of_month} {faults == work_days_of_month} WEDM:{worked_days_of_month} QM:{qtd_max}')

        return faults if faults < qtd_max else qtd_max
