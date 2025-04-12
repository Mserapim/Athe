# -*- coding: utf-8 -*-

from django.db.models import Q, Sum

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import BaseCalculation
from standard.models import RunCodeManager

log = getLogger(__name__)


class BasePension(BaseCalculation):
    title = "Cálculo base de pensão!"
    description = "Calculo autmático para pensão"

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False
    FORCE_RECALCULATE_BASE = True
    MEMORY = True

    @property
    def pensions(self):
        query = self.employee.pensao_pagador.exclude(
            Q(data_inicio__gt=self.range_salary.last)
            | (~Q(data_fim=None) & Q(data_fim__lt=self.range_salary.first))
        ).filter(
            Q(type_of_pension__in=[1, 2])
            & (
                Q(event_employee=self.event)
                |
                # TODO Precisa garantir que folha de 13º utilize apenas o evento event_employee_13 e a mensão apenas event_employee
                Q(event_employee_13=self.event)
                | Q(event_pensioner=self.event)
            )
        )
        return query

    @property
    def pension(self):
        return (
            self.pensions.filter(pensionista=self.object)
            .order_by("-data_inicio")
            .first()
        )


@RunCodeManager.register("gfp-mpto-pension-employee")
class PensionEmployee(BasePension):
    title = "Pensão paga pelo servidor"
    description = "Cálculo automático para pensão paga pelo servidor."

    FILTER_QUERY = 1
    FILTER_BY = 2

    def validate(self):
        self.validate_not_paycheck_pension()
        # log.debug('VALIDATE PENSION...')
        # log.debug(self.base_value_query())
        if not self.base_value_query().exists():
            raise self.CalculationNotApplicable(
                "Contracheque não possui nenhum dos eventos configurado na(s) pensão(ões)!"
            )

    @property
    def focuses_on(self):
        # log.debug('FOCUSES_ON...')
        focuses_on = []
        if self.object:
            focuses_on = [ev.numero for ev in self.pension.events.all()]
        else:
            for p in self.pensions:
                for ev in p.events.all():
                    focuses_on.append(ev.numero)
        # log.debug(f'>>>> {focuses_on} do {self.event.numero}')
        return focuses_on

    def _get_focuses_on(self):
        return self.focuses_on

    def _get_query(self):
        query = self.pensions
        if "oIds" in self.params:
            query = query.filter(pensionista__in=self.params["oIds"])
        return [p.pensionista for p in query]

    def event_information(self):
        return self.object.pessoafisica.abbreviation

    def used_value_of_pension(self, value):
        new_value = float(
            self.payroll.lancamentos.filter(
                contracheque__servidor=self.employee,
                contracheque__pensioner=self.object,
                entry_pension__contracheque__servidor=self.employee,
                entry_pension__contracheque__pensioner__isnull=True,
            )
            .aggregate(total=Sum("value"))
            .get("total")
            or 0.00
        )

        return new_value

    @cache_return
    def base_value(self):
        if not self.object:
            return 0.0
        if self.pension.tipo == 1:
            base_value = float(self.pension.valor)
        elif self.pension.tipo == 2:
            self.only_events = []
            base_value = super(PensionEmployee, self).base_value()
        elif self.pension.tipo == 3:
            base_value = float(self.payroll.periodo.salario_minimo)
        return base_value

    @cache_return
    def percentage(self):
        if not self.object:
            return 0.0
        if self.pension.tipo == 1:
            pct = 100.0
        elif self.pension.tipo == 2:
            pct = float(self.pension.valor)
        else:
            pct = float(self.pension.valor) * 100.0

        return pct

    @cache_return
    def value(self):
        value = super(PensionEmployee, self).value()
        if self.object and self.pension.type_of_pension == 2:
            value = self.used_value_of_pension(value)

        return value


@RunCodeManager.register("gfp-mpto-pension-employee-cash-basis")
class PensionEmployeeCashBasis(PensionEmployee):

    def _get_value_from_entry(self, entry):
        if (
            self.FULL_VALUE and entry.evento.numero not in self.FORCE_PAID_VALUE
        ) or entry.evento.numero in self.FORCE_FULL_VALUE:
            value = entry.valor * (entry.qnt_max / entry.qnt)
        else:
            value = entry.valor
        return float(value)

    def _get_focuses_on(self):
        fo = list(self.focuses_on)
        fo.append(self.event.numero)
        return fo


@RunCodeManager.register("gfp-mpto-pension-pensioner")
class PensionPensioner(BasePension):
    title = "Pensão recebida pelo pensionista"
    description = "Calculo autmático para pensão recebida pelo pensionista."

    MULTI_CALCULATE = False
    JOIN_ON_MULTI = False
    FORCE_RECALCULATE_BASE = False

    def validate(self):
        # log.debug(self.pensions.count())
        if not self.pensioner or self.pensions.filter(type_of_pension=2).exists():
            raise self.CalculationNotApplicable(
                "Cálculo apenas para pensionistas de alimentação!"
            )

    def base_value_query(self):
        if not self.pensioner:
            return []

        abbreviation = self.pensioner.abbreviation
        pension = self.pensioner.pensao_pensionista.filter(
            Q(data_inicio__lte=self.payroll.date_range.last)
            & (Q(data_fim=None) | Q(data_fim__gte=self.payroll.date_range.first))
        ).first()
        event = (
            pension.event_employee_13 if self.month == 13 else pension.event_employee
        )
        q_entries = Q(
            evento__genre_event=event.genre_event,
            contracheque__servidor=self.employee,
            contracheque__pensioner=None,
            info=abbreviation,
        )
        if self.exclude_events:
            q_entries = Q(q_entries & ~Q(evento__numero__in=self.exclude_events))
        if self.only_events:
            q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))

        return self.reference_payroll.lancamentos.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )

    @cache_return
    def base_value(self):
        base_value = super(PensionPensioner, self).base_value() * -1

        return base_value
