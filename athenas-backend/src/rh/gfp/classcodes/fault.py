# -*- coding: utf-8 -*-

from contrib.decorator import cache_return
from contrib.utils import getLogger
from django.db import models
from rh.gfp.classcodes.base import BaseCalculation
from rh.gfp.models import ExtraPaymentPeriod
from rh.ponto.models import Falta
from standard.models import RunCodeManager

DIASCOMERCIAL = 30

log = getLogger(__name__)


@RunCodeManager.register("gfp-classcodes-fault")
class Fault(BaseCalculation):

    title = "Cálculo de faltas"

    FULL_VALUE = True

    @property
    @cache_return
    def object(self):
        # log.debug(self.get_query())
        if len(self.get_query()) == 1 or len(set(self.get_query())) == 1:
            return self.get_query()[0]
        return None

    @cache_return
    def quantity(self):
        return self.get_faults()

    def get_faults(self):
        faltas = Falta.objects.filter(
            servidor=self.employee,
            injustificada__gt=0,
            data__range=(self.payroll.date_range.first, self.payroll.date_range.last),
        )
        fault_days = 0
        for f in faltas:
            fault_days += (
                float(f.injustificada)
                / 60.0
                / (float(f.carga_horaria.quantidade) / 5.0)
            )

        return round(fault_days, 3)

    def maximum_quantity(self):
        return self.payroll.date_range.days

    def base_socialsecurity(self):
        return self.value()


class BaseHours(BaseCalculation):

    title = "Cálculo de Horas Negativas"

    FULL_VALUE = True

    FORCE_RECALCULATE_BASE = True

    @property
    @cache_return
    def object(self):
        # log.debug(self.get_query())
        if len(self.get_query()) == 1 or len(set(self.get_query())) == 1:
            return self.get_query()[0]
        return None

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

    def _get_value_from_calc(self, calc, full_value=False):
        return calc.value() if not calc.full_value else calc.base_value()

    def _get_base_ss_from_calc(self, calc):
        return 0

    @property
    def base_ceiling(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )


@RunCodeManager.register("gfp-classcodes-negative-hours")
class NegativeHours(BaseHours):

    def get_faults(self):
        faltas = Falta.objects.filter(
            servidor=self.employee,
            horas_negativas__gt=0,
            data__range=(self.payroll.date_range.first, self.payroll.date_range.last),
        )
        fault_days = 0
        for f in faltas:
            fault_days += float(f.horas_negativas) / 60.0

        return round(fault_days, 2)

    def full_value(self):
        return self.value()


@RunCodeManager.register("gfp-classcodes-positive-hours")
class PositiveHours(BaseHours):

    def get_faults(self):
        faltas = Falta.objects.filter(
            servidor=self.employee,
            horas_positivas__gt=0,
            data__range=(self.payroll.date_range.first, self.payroll.date_range.last),
        )
        fault_days = 0
        for f in faltas:
            fault_days += float(f.horas_positivas) / 60.0

        return round(fault_days, 2)

    def percentage(self):
        return 150.00


@RunCodeManager.register("gfp-classcodes-fault-aid-supply")
class AidSupplyFault(Fault):

    def maximum_quantity(self):
        return 22

    def base_value(self):
        q = ExtraPaymentPeriod.objects.filter(
            extra_payment__slug="AUXILIO-ALIMENTACAO"
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return round(float(q[0].value), 2) if q.exists() else 0.00
