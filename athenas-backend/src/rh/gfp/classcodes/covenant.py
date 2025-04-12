# -*- coding: utf-8 -*-

import datetime

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.classcodes.base import BaseCalculation, WorkDaysCalculation
from standard.models import RunCodeManager

log = getLogger(__name__)


class CovenantBase(BaseCalculation):
    pass


@RunCodeManager.register("gfp-classcodes-sindsemp")
class SindSEMP(CovenantBase):

    title = "Cálculo SindSEMP"

    def percentage(self):
        pct = super(SindSEMP, self).percentage()
        log.debug("PERCENTAGE SindSEMP: %s" % pct)
        return pct


@RunCodeManager.register("gfp-classcodes-fenasemp")
class Fenasemp(WorkDaysCalculation):
    FULL_VALUE = True
    MULTI_CALCULATE = False
    FORCE_RECALCULATE_BASE = True

    def validate(self):
        if "EF" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não é efetivo no período" % (self.employee)
            )

    def quantity(self):
        return 1

    def event_information(self):
        return "REF. %s" % datetime.datetime.now().year


@RunCodeManager.register("gfp-classcodes-asamp")
class ASAMP(CovenantBase):

    title = "Cálculo ASAMP"

    PARAMS_ = ["info"]


@RunCodeManager.register("gfp-classcodes-atmp")
class ATMP(BaseCalculation):

    title = "Cálculo ATMP"

    def value(self):
        from math import trunc

        return trunc(super(ATMP, self).value() * 100) / 100.0


@RunCodeManager.register("gfp-classcodes-atmp-13salario")
class ATMP13Salary(ATMP):

    title = "Cálculo ATMP 13° Salário"

    def maximum_days_quantity(self):
        return 12

    @cache_return
    def quantity(self):
        if self.employee.posses.order_by("-data_exercicio").exists():
            posse = self.employee.posses.order_by("data_exercicio")[0]
            if posse.data_exercicio.year < self.payroll.periodo.ano:
                r = 12.00
            elif posse.data_exercicio.year == self.payroll.periodo.ano:
                qnt = 12 - posse.data_exercicio.month
                qnt = qnt if posse.data_exercicio.day > 15 else qnt + 1

                r = float(qnt)
            else:
                log.info(
                    "O servidor %s não tem direito a 13° para %s"
                    % (self.employee.pessoa_fisica, self.payroll)
                )
                r = 0.00
        else:
            log.info(
                "O servidor %s servidor não tem posse." % self.employee.pessoa_fisica
            )
            r = 0.00

        log.debug("ATMP 13 Salario Quantidade: %s." % r)
        return r


@RunCodeManager.register("gfp-classacodes-plansaude-monthly-payment")
class PlanSaudeMonthlyPayment(BaseCalculation):

    title = "Cálculo PlanSaúde"

    PARAMS_ = ["qnt", "info"]

    @property
    @cache_return
    def object(self):
        log.debug(self.get_query())
        if len(self.get_query()) == 1 or len(set(self.get_query())) == 1:
            return self.get_query()[0]
        return None

    def percentage(self):
        return 6.00 if self.quantity() > 0 else 4.00

    @property
    def max_payment_employer(self):
        if (
            self.payroll.periodo.ano < 2017
            or self.payroll.periodo.ano == 2017
            and self.payroll.periodo.mes <= 5
        ):
            return float(self.payroll.periodo.salario_minimo) * 0.46
        else:
            return float(self.payroll.periodo.salario_minimo) * 0.6853

    @property
    @cache_return
    def minimum_payment(self):
        return (
            ((float(self.event.current_config.ceiling) * 0.46) / 0.06)
            if self.event.current_config.ceiling
            else float(self.payroll.periodo.salario_minimo) * 0.46
        )

    def employer_value(self):
        pat = (
            max(round(self.max_payment_employer - self.value(), 2), 0.00)
            if self.value()
            else 0.00
        )
        return pat

    @property
    @cache_return
    def floor(self):
        return (
            float(self.event.current_config.ceiling)
            if self.event.current_config.ceiling
            else 0.06 * float(self.payroll.periodo.salario_minimo)
        )

    @property
    @cache_return
    def ceiling(self):
        return (
            float(self.event.current_config.floor)
            if self.event.current_config.floor
            else 10.0 * self.floor
        )
