# -*- coding: utf-8 -*-

import math

from django.db.models import Sum

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import BaseCalculation
from standard.models import RunCodeManager

log = getLogger(__name__)

BUSINESSDAYS = 30


@RunCodeManager.register("mpto-gfp-difference")
class Differences(BaseCalculation):
    typeof = "CALCULO"
    title = "Cálculo de diferenças"
    description = "Este cálculo será usado pelo Gestor de Diferenças do Athenas para calcular os pagamentos parcelados\
                   que são percentuais sobre algumas rubricas ou salário mínimo"

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "oIds", "installment"]

    """
    MULTI_CALCULATE = Truecalc
    Usado para definir se o calculo será executado para cada elemento do get_query()
    """
    MULTI_CALCULATE = False

    JOIN_ON_MULTI = False

    FORCE_RECALCULATE_BASE = False

    EVALUATE_ON_REFERENCE_PAYROLL = False
    # CALCULATE_OVER = 3

    FULL_VALUE = False

    def __init__(self, employee, payroll, event=None, **kwargs):
        """
        Inicializador do calculo, recebe o servidor, folha a ser calculada e o evento que possui o calculo automático.
        """
        # log.debug('KWARGS: %s' % kwargs)
        self.difference = kwargs.get("difference", None)
        super(Differences, self).__init__(employee, payroll, event, **kwargs)
        if self.entry and not self.difference:
            self.difference = self.entry.paycheck_difference

    def configure(self):
        pass

    @property
    def payable(self):
        if self.difference:
            if (
                self.difference.total_value
                or self.difference.total_employer_contribution
            ):
                pp = {
                    "value": self.difference.total_value,
                    "employer_contribution": self.difference.total_employer_contribution,
                }
            else:
                pp = self.difference.difference_items.aggregate(
                    value=Sum("fixed_value")
                )
            paid = self.difference.entries_payment.filter(
                contracheque__folha__lt=self.payroll
            ).aggregate(value=Sum("value"))

            return round((pp["value"] or 0) - (paid["value"] or 0), 2)

    @property
    def ceiling(self):
        if self.difference:
            return abs(self.payable)

        return (
            float(self.event.ceiling_at(self.range_salary.first))
            if self.event and self.event.ceiling_at(self.range_salary.first)
            else 9999999.99
        )

    @property
    def focuses_on(self):
        focuses_on = []
        if self.difference:
            focuses_on = [e.numero for e in self.difference.focuses_on.all()]
        if self.only_events:
            focuses_on = [
                event_number
                for event_number in focuses_on
                if event_number in self.only_events
                and event_number not in self.exclude_events
            ]
        return focuses_on

    def base_value(self):
        base_value = 0
        if self.difference:
            if self.config_to_next_installment:
                if self.config_to_next_installment.typeof == 1:
                    base_value = abs(float(self.difference.total_value))
                elif self.config_to_next_installment.typeof == 3:
                    base_value = float(self.payroll.periodo.salario_minimo)
                else:
                    base_value = super(Differences, self).base_value()
        return base_value

    @cache_return
    def value(self):
        value = 0
        if self.difference:
            if (
                self.config_to_next_installment
                and self.config_to_next_installment.typeof == 1
            ):
                value = float(self.config_to_next_installment.value)
            else:
                value = super(Differences, self).value()

        if value:
            value = min(value, self.ceiling)
            value = max(value, self.floor)
        return value

    @cache_return
    def employer_value(self):
        value = 0
        if self.difference:
            if (
                self.config_to_next_installment
                and self.config_to_next_installment.typeof == 1
            ):
                value = float(self.config_to_next_installment.employer_contribution)
            else:
                value = super(Differences, self).employer_value()

        # if value:
        #     value = min(value, self.ceiling)
        #     value = max(value, self.floor)
        return value

    @cache_return
    def event_information(self):
        if "info" in self.params:
            return self.params["info"]
        return ""

    def validate(self):
        self.validate_not_paycheck_pension()

    def callback(self, **kargs):
        log.debug("CALLBACK for %s" % self.__class__.__name__)

    def _get_query(self):
        return []

    def choices(self):
        return [
            (obj.pk if hasattr(obj, "pk") else obj, self.unicode_for_obj(obj))
            for obj in self.get_query()
        ]

    @property
    @cache_return
    def object(self):
        if len(self.get_query()) == 1:
            return self.get_query()[0]
        return None

    def get_params_for_obj(self, obj):
        return {"oIds": [obj.pk if hasattr(obj, "pk") else obj]}

    def unicode_for_obj(self, obj):
        return str(obj)

    @cache_return
    def percentage(self):
        pct = 100
        if self.difference and self.difference.installments > 1:
            config = self.config_to_next_installment
            if config.typeof == 2:
                pct = float(config.value)
            elif config.typeof == 3:
                pct = float(config.value * 100)
        return pct

    @property
    def next_intallment_to_pay(self):
        if self.difference:
            qnt = (
                self.difference.entries_payment.exclude(
                    contracheque__folha=self.payroll
                )
                .aggregate(qnt=Sum("installments_paid"))
                .get("qnt")
                or 0
            ) + 1
            log.debug("NIP: %s" % qnt)
            return qnt
        return 0

    @property
    def config_to_next_installment(self):
        installment = self.installment
        return (
            self.difference.differences_config.exclude(
                initial_installment__gt=installment
            )
            .order_by("initial_installment")
            .last()
        )

    def installment(self):
        installment = self.next_intallment_to_pay
        if self.params.get("installment") and self.lancamento == "T":
            installment = int(self.params["installment"])
        elif self.entry:
            installment = self.entry.parcela
        # log.debug('PORCENTAGEM de BaseCalculo: %s' % installment)
        return installment

    def installments_paid(self):
        installments_paid = 0
        if self.difference:
            installments_paid = 1
        if self.params.get("installments_paid") and self.lancamento == "T":
            installments_paid = int(self.params["installments_paid"])
        elif self.entry:
            installments_paid = self.entry.installments_paid

        # log.debug('PORCENTAGEM de BaseCalculo: %s' % installment)
        return installments_paid

    def total_installment(self):
        total_installment = 0
        log.debug(
            "TI: %s DIFF: %s" % (self.params.get("total_installment"), self.difference)
        )
        if self.difference and self.difference.installments > 1:
            # if self.config_to_next_installment.typeof in [2, 3]:
            log.debug("TI >> %s: %s" % (self.payable, self.value()))
            total_installment = math.ceil(abs(self.payable / self.value()))
            total_installment += self.installment() - 1
            # else:
            #     total_installment = int(self.difference.installments)
        elif self.params.get("total_installment") and self.lancamento == "T":
            total_installment = int(self.params["total_installment"])
        log.debug("TI: %s DIFF: %s" % (total_installment, self.difference))
        # log.debug('PORCENTAGEM de BaseCalculo: %s' % installment)
        return total_installment
