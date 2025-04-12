from django.db.models import Q
from contrib.utils import getLogger

from rh.gfp.calcs.mpmt.base import WorkDaysCalculation

from standard.models import RunCodeManager
from rh.gfp.models import ConfigEvent

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpmt-faltabolsaresidente")
class FaltaBolsaResidente(WorkDaysCalculation):
    title = "Cálculo Base para desconto de Falta(s) de Residente"

    def buscar_contracheque(self):
        q_cc = self.payroll.paychecks.filter(servidor=self.employee)

        return q_cc.first() if q_cc.exists() else None

    def buscar_fe_bolsa_residente(self, cc):
        q_fe = cc.lancamentos.filter(evento__numero="12200")  # Bolsa Residente

        return q_fe.first() if q_fe.exists() else None

    # def buscar_config_evento_vigente(self, dt_inicio, dt_fim):
    #     q_config_event = ConfigEvent.objects.filter(
    #         event__numero='12200', # Bolsa Residente
    #         start_validity__lte=dt_fim,
    #     ).filter(
    #         Q(end_validity__isnull=True) |
    #         Q(end_validity__gte=dt_inicio)
    #     )

    #     return q_config_event.order_by('-start_validity').first() if q_config_event.exists() else None

    # def base_value(self):
    #     dt_inicio = self.range_salary.first
    #     dt_fim = self.range_salary.last
    #     q_config_event = self.buscar_config_evento_vigente(dt_inicio, dt_fim)

    #     if q_config_event is None:
    #         return 0.00
    #     else:
    #         return float(q_config_event.base_value)

    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)

        return 0.00

    def maximum_quantity(self):
        if self.event and self.event.max_quantity_at(self.range_salary.first):
            return float(self.event.max_quantity_at(self.range_salary.first))
        else:
            return (
                self.base_days
                if not self._is_christmas_grat
                else self.event.max_quantity_at(self.range_salary.first)
            )

    def value(self):
        value = (self.base_value() / self.maximum_quantity()) * self.quantity()

        return value

    def validar_residente(self):
        if self.employee.type_by_possession != "RES":
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada a residentes!"
            )

    def validate(self):
        self.validar_residente()


@RunCodeManager.register("gfp-mpmt-faltatransporteresidente")
class FaltaTransporteResidente(WorkDaysCalculation):
    title = "Cálculo Base para desconto de Falta(s) de Residente no Aux. Transporte"

    def buscar_contracheque(self):
        q_cc = self.payroll.paychecks.filter(servidor=self.employee)

        return q_cc.first() if q_cc.exists() else None

    def buscar_fe_transporte_residente(self, cc):
        q_fe = cc.lancamentos.filter(evento__numero="12300")  # Transporte Residente

        return q_fe.first() if q_fe.exists() else None

    # def buscar_config_evento_vigente(self, dt_inicio, dt_fim):
    #     q_config_event = ConfigEvent.objects.filter(
    #         event__numero='12300', # Transporte Residente
    #         start_validity__lte=dt_fim,
    #     ).filter(
    #         Q(end_validity__isnull=True) |
    #         Q(end_validity__gte=dt_inicio)
    #     )

    #     return q_config_event.order_by('-start_validity').first() if q_config_event.exists() else None

    # def base_value(self):
    #     dt_inicio = self.range_salary.first
    #     dt_fim = self.range_salary.last
    #     q_config_event = self.buscar_config_evento_vigente(dt_inicio, dt_fim)

    #     if q_config_event is None:
    #         return 0.00
    #     else:
    #         return float(q_config_event.base_value)

    def quantity(self):
        if self.event:
            log.info(f"self.params: {self.params}")
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)

        return 0.00

    def maximum_quantity(self):
        if self.event and self.event.max_quantity_at(self.range_salary.first):
            return float(self.event.max_quantity_at(self.range_salary.first))
        else:
            return (
                self.base_days
                if not self._is_christmas_grat
                else self.event.max_quantity_at(self.range_salary.first)
            )

    def value(self):
        value = (self.base_value() / self.maximum_quantity()) * self.quantity()

        return value

    def validar_residente(self):
        if self.employee.type_by_possession != "RES":
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada a residentes!"
            )

    def validate(self):
        self.validar_residente()
