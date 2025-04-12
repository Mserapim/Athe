from decimal import Decimal
from calendar import monthrange
from datetime import datetime

from contrib.utils import getLogger
from django.db.models import Q

from rh.gfp.calcs.mpmt.base import WorkDaysCalculation

from standard.models import RunCodeManager
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.models import MovimentacaoTeletrabalho

from contrib.daterange import NewDateRange
from rh.const import CANCELADO as AFASTAMENTO_CANCELADO, TYPE_HEALTHHOURS

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpmt-baseresidente")
class BaseResidente(WorkDaysCalculation):
    title = "Cálculo Base para remuneração de Residente"

    def validar_residente(self):
        if self.employee.type_by_possession != "RES":
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada a residentes!"
            )

    def validate(self):
        self.validar_residente()

    def maximum_quantity(self):
        if self.event and self.event.max_quantity_at(self.range_salary.first):
            return float(self.event.max_quantity_at(self.range_salary.first))
        else:
            return (
                self.base_days
                if not self._is_christmas_grat
                else self.event.max_quantity_at(self.range_salary.first)
            )

    def quantity(self):
        qtd = (
            self.range_salary_for().business_days
            if self.BASE_BUSINESSDAYS
            else self.range_salary_for().days
        )

        if qtd > self.maximum_quantity():
            qtd = self.maximum_quantity()

        return qtd


@RunCodeManager.register("gfp-mpmt-transporte-residente")
class AuxilioTransporteResidente(WorkDaysCalculation):
    title = "Cálculo Base para Auxílio Transporte de Residente"

    def range_salary_for(
        self, possession=None, range_salary=None, get_possessions_from13=False
    ):
        if not range_salary:
            range_salary = self._intersect_ranges_for_range_salary()
        ranges_ = NewDateRange()

        if range_salary.days == 0:
            return ranges_
        get_possessions = (
            self.get_possessions()
            if not get_possessions_from13
            else self.get_possessions_13()
        )
        if not possession:
            for possession in get_possessions:
                dt_end = (
                    possession.financial_effect_date_end
                    if possession.financial_effect_date_end
                    else None
                )
                ranges_ += NewDateRange(possession.financial_effect_date_start, dt_end)
        else:
            dt_end = (
                possession.financial_effect_date_end
                if possession.financial_effect_date_end
                else None
            )
            ranges_ += NewDateRange(possession.financial_effect_date_start, dt_end)

        ranges_ = ranges_.intersect(range_salary)
        return ranges_

    def maximum_quantity(self):
        if self.event and self.event.max_quantity_at(self.range_salary.first):
            return float(self.event.max_quantity_at(self.range_salary.first))
        else:
            return (
                self.base_days
                if not self._is_christmas_grat
                else self.event.max_quantity_at(self.range_salary.first)
            )

    def quantity(self):
        qtd = (
            self.range_salary_for().business_days
            if self.BASE_BUSINESSDAYS
            else self.range_salary_for().days
        )

        if qtd > self.maximum_quantity():
            qtd = self.maximum_quantity()

        return qtd

    def validar_residente(self):
        if self.employee.type_by_possession != "RES":
            raise self.CalculationNotApplicable(
                "Esta verba só pode ser aplicada a residentes!"
            )

    def validate(self):
        self.validar_residente()


@RunCodeManager.register("gfp-mpmt-transporte-residente-desconto-afastamento")
class DescontoAfastamentoAuxilioTransporteResidente(BaseResidente):
    title = "Cálculo para Desconto com base em Afastamentos para Auxílio Transporte de Residente"

    def maximum_quantity(self):
        """
        Método responsável por definir a quantidade máxima de dias do mês para utilizar no cálculo.
        A regra é que seja utilizado o valor que estiver definido nas configurações da verba, caso não encontre
        será utilizado a quantidade de dias do mês a ser calculado.
        """

        if self.event and self.event.max_quantity_at(self.range_salary.first):
            return float(self.event.max_quantity_at(self.range_salary.first))
        else:
            return (
                self.base_days
                if not self._is_christmas_grat
                else self.event.max_quantity_at(self.range_salary.first)
            )

    def buscar_contracheque(self):
        return self.payroll.paychecks.filter(servidor=self.employee).first()

    def buscar_evento_contracheque(self, evento_numero, info=None):
        contracheque = self.buscar_contracheque()
        q_cc = contracheque.lancamentos.filter(evento__numero=evento_numero)

        if info is not None:
            q_cc = q_cc.filter(info=info)

        return q_cc

    def quantity(self):
        """
        Método responsável por determinar a quantidade de dias que deve ser calculado.
        Como é uma verba de desconto, a quantidade de dias de afastamentos será utilizada no cálculo.

        Essa verba tem o comportamento sobre descontos diferente de outras verbas, ela precisa computar
        os valores de cada afastamento individualmente.
        """

        if "qnt" in self.params and self.params["qnt"] not in ["", "0", 0]:
            return self.params["qnt"]

        dias_afastamento = 0
        range_afastamentos = NewDateRange()

        for mc in AfastamentoOutroOrgao.objects.filter(servidor=self.employee).exclude(
            Q(data_inicio__gt=self.range_salary.last)
            | Q(onus=1)
            | Q(transito_pela_folha=True)
            | Q(estado=AFASTAMENTO_CANCELADO)
        ):
            range_afastamentos = NewDateRange(mc.data_inicio, mc.data_fim)
            info = mc.get_tipo_display()
            q_cc = self.buscar_evento_contracheque("12302", info)
            if dias_afastamento == 0 and q_cc.exists() is False:
                dias_afastamento = range_afastamentos.days
                self.params["info"] = info

        if dias_afastamento == 0:
            ultimo_dia_mes = monthrange(self.year, self.month)[1]
            dt_ini_folha = datetime(self.year, self.month, 1).date()
            dt_fim_folha = datetime(self.year, self.month, ultimo_dia_mes).date()
            range_folha = NewDateRange(dt_ini_folha, dt_fim_folha)

            for absence in (
                BaseLicencaAfastamento.objects.filter(
                    # remunerado=False,
                    servidor=self.employee
                )
                .exclude(
                    Q(data_fim__lt=self.range_salary.first)
                    | Q(data_inicio__gt=self.range_salary.last)
                )
                .exclude(~Q(afastamento__afastamentooutroorgao=None))
                .exclude(estado=AFASTAMENTO_CANCELADO)
                .exclude(tipo=TYPE_HEALTHHOURS)
            ):  # Licença Saúde Horas:
                query_tele = MovimentacaoTeletrabalho.objects.filter(
                    servidor=self.employee,
                    data_inicio__lte=absence.data_fim,
                    data_fim__gte=absence.data_inicio,
                )

                if query_tele.exists():
                    tele = query_tele.first()

                    if tele.data_inicio < dt_ini_folha:
                        dt_ini_tele = dt_ini_folha
                    else:
                        dt_ini_tele = tele.data_inicio

                    if tele.data_fim > dt_fim_folha:
                        dt_fim_tele = dt_fim_folha
                    else:
                        dt_fim_tele = tele.data_fim
                    range_tele = NewDateRange(dt_ini_tele, dt_fim_tele)

                    if absence.data_inicio < dt_ini_folha:
                        dt_ini_afa = dt_ini_folha
                    else:
                        dt_ini_afa = absence.data_inicio

                    if absence.data_fim > dt_fim_folha:
                        dt_fim_afa = dt_fim_folha
                    else:
                        dt_fim_afa = absence.data_fim
                    range_afastamentos = NewDateRange(dt_ini_afa, dt_fim_afa)

                    range_disponivel = range_folha - range_tele
                    range_desconto = range_disponivel.intersect(range_afastamentos)
                    info = absence.get_tipo_display()
                    q_cc = self.buscar_evento_contracheque("12302", info)
                    if dias_afastamento == 0 and q_cc.exists() is False:
                        dias_afastamento = range_desconto.days
                        self.params["info"] = info
                else:
                    range_afastamentos = NewDateRange(
                        absence.data_inicio, absence.data_fim
                    )
                    info = absence.get_tipo_display()
                    q_cc = self.buscar_evento_contracheque("12302", info)
                    if dias_afastamento == 0 and q_cc.exists() is False:
                        range_desconto = range_folha.intersect(range_afastamentos)
                        dias_afastamento = range_desconto.days
                        self.params["info"] = info

        return (
            self.maximum_quantity()
            if dias_afastamento > self.maximum_quantity()
            else dias_afastamento
        )

    def base_value(self):
        """
        Método responsável por determinar qual é o valor base de cálculo da verba.
        A regra é que deve ser o mesmo valor base da verba 12300 - AUXÍLIO TRANSPORTE RESIDENTES do mês que está sendo calculado
        """

        if "base_value" in self.params:
            return float(self.params["base_value"])

        valor_base = 0
        q_cc = self.buscar_evento_contracheque("12300")
        if q_cc.exists():
            valor_base = q_cc.first().valor_base

        return float(valor_base)


@RunCodeManager.register("gfp-mpmt-transporte-residente-desconto-teletrabalho")
class DescontoTeletrabalhoAuxilioTransporteResidente(BaseResidente):
    title = "Cálculo para Desconto no Período de Teletrabalho para Auxílio Transporte de Residente"

    def q_evento_aux_transp(self):
        contracheque = self.employee.paychecks.filter(folha=self.payroll)

        return contracheque.first().lancamentos.filter(evento__numero="12300")

    def quantity(self):
        range_periodo = NewDateRange()

        range_teletrabalho = NewDateRange()
        for teletrabalho in MovimentacaoTeletrabalho.objects.filter(
            servidor=self.employee
        ).exclude(
            Q(data_fim__lt=self.range_salary.first)
            | Q(data_inicio__gt=self.range_salary.last)
        ):
            range_teletrabalho = NewDateRange(
                teletrabalho.data_inicio, teletrabalho.data_fim
            )
            range_teletrabalho_intersec = range_teletrabalho.intersect(
                self.range_salary
            )
            if range_teletrabalho_intersec.days > 0:
                range_periodo += range_teletrabalho_intersec

        return 0 if range_periodo.days < 0 else range_periodo.days

    def base_value(self):
        evento_aux_transp = self.q_evento_aux_transp().first()

        return evento_aux_transp.valor_base

    def event_information(self):
        return "TELETRABALHO"

    def value(self):
        return (self.base_value() / Decimal(self.range_salary.days)) * self.quantity()

    def validar_presenca_verba_aux_transporte(self):
        if self.q_evento_aux_transp().exists() is False:
            raise self.CalculationNotApplicable(
                "O Residente não tem a verba de Auxílio Transporte!"
            )

    def validate(self):
        super().validar_residente()
        self.validar_presenca_verba_aux_transporte()
