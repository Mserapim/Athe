# -*- coding: utf-8 -*-

from django.db.models import Max, Q, Count

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import BaseCalculation
from rh.gfp.models import (
    IRRF as IRRFModel,
    FolhaEvento as Entry,
    RRA,
    IRRFFaixa,
    RRAServidorFolhaTipo,
)
from rh.models import Dependencia, ProcessSuspension
from standard.models import RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpto-irrf")
class IRRF(BaseCalculation):
    title = "Calculo de imposto retido na fonte"

    ALL_PAYROLL = True
    RRA_CALC = False

    DISCOUNT_DESC = "DESCONTO DEPENDENTES"
    MEMORY = True

    RECALCULATE_BASES = 2

    def __init__(self, employee, payroll, event=None, entry=None, cid=None, **kwargs):
        """
        Inicializador do calculo, recebe o servidor, folha a ser calculada e o evento que possui o calculo automático.
        """
        super(IRRF, self).__init__(employee, payroll, event, entry, cid=cid, **kwargs)
        if self.suspension:
            self.exclude_events += [
                ev.numero for ev in self.suspension.process.gfp_events.all()
            ]
            # log.debug("CHANGING EXCLUDED EVENTS TO %s" % self.exclude_events)

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

        return obj

    @cache_return
    def quantity(self):
        return Dependencia.objects.irrf_actives(
            self.employee, self.range_salary.last
        ).count()

    @cache_return
    def discount_dependent(self):
        irrf = self.irrf()
        vl = float(irrf.valor_dependente)
        return self.quantity() * vl

    def base_discounts(self):
        return self.discount_dependent()

    def percentage(self):
        irrf_range = self.range()
        return irrf_range["percentage"]

    def base_value_query(self):
        query = super(IRRF, self).base_value_query()
        if not self.RRA_CALC:
            return query.filter(rra_employee__isnull=True)
        else:
            if self.object:
                return query.filter(rra_employee__rra=self.object)
            else:
                return query.none()
        return query

    def _get_value_from_entry(self, entry):
        if (
            self.FULL_VALUE and entry.evento.numero not in self.FORCE_PAID_VALUE
        ) or entry.evento.numero in self.FORCE_FULL_VALUE:
            value = entry.valor * (entry.qnt_max / entry.qnt)
        else:
            value = entry.valor
        return float(value)

    def set_memory_range(self):
        self.set_memory(f"FAIXA = {self.percentage()}%")

    @cache_return
    def value(self):
        if (
            self.employee.molestia
            and self.employee.molestia.data_laudo < self.range_salary.last
        ):
            return 0.00
        base = self.base_value()
        range_ir = self.range()
        base_1 = base * range_ir["percentage"] / 100.0
        self.set_memory_range()
        value = base_1 - range_ir.get("discount", 0.00)
        self.set_memory(
            f'BASE IR = {base:0.2f} x {range_ir["percentage"]}% = {base_1:0.2f}'
        )
        self.set_memory(
            f'VALOR IR = {base_1:0.2f} - {range_ir.get("discount", 0.00)}(DEDUTOR FAIXA) = {value:0.2f}'
        )
        discount_paid = self.discount_paid_other_payroll(value_field="valor")
        if discount_paid:
            i_value = value
            value -= self.discount_paid_other_payroll(value_field="valor")
            self.set_memory(
                f"VALOR IR = {i_value:0.2f} - {discount_paid}(IR JÁ APURADO) = {value:0.2f}"
            )
        return value


@RunCodeManager.register("gfp-mpto-irrf-rra")
class IRRFRRA(IRRF):
    titulo = "Calculo de imposto retido na fonte com RRA"

    MULTI_CALCULATE = True
    RRA_CALC = True

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

    def _get_query(self):
        if self.params.get("oIds"):
            return RRA.objects.filter(pk__in=self.params.get("oIds"))

        return RRA.objects.annotate(
            fes=Count(
                "employeers__entries",
                filter=Q(
                    employeers__entries__folha=self.payroll,
                    employeers__employee=self.employee,
                ),
            )
        ).filter(fes__gt=0)

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
        installments = installments_paid = months = 0
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
                return (
                    (float(months) / float(installments)) * float(installments_paid),
                    installments,
                    installments_paid,
                    months,
                )
        return 0, installments, installments_paid, months

    def range(self):
        try:
            irrf = self.irrf()
            rra_quantity = float(self.rra_factor[0])
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
                f"Base IRRF: {normatized_base_value}. Utilizando a faixa isenta do IRRF!"
            )
        except Exception as e:
            log.exception(e)
        else:
            obj["percentage"] = float(range_.percentual)
            obj["discount"] = float(range_.desconto) * rra_quantity

        # log.debug('IRRF %s: RRA %s: BV %s: NBV %s: RP %s: RD %s: NRD %s' % (irrf, rra_quantity, self.base_value(
        # ), normatized_base_value, range_.percentual, range_.desconto, obj["discount"]))

        return obj

    def set_memory_range(self):
        factor, installments, installments_paid, months = self.rra_factor
        sub_memory = []

        query_base = self.payroll.lancamentos.filter(
            servidor=self.employee, rra_employee__isnull=False
        ).order_by("reference_year", "reference_month")
        query_events = query_base.values("reference_month", "reference_year").distinct()
        if query_events.exists():
            idx = 1
            for k in query_events:
                events = set(
                    [
                        fe.evento.numero
                        for fe in query_base.filter(
                            reference_year=k["reference_year"],
                            reference_month=k["reference_month"],
                        ).order_by("evento__numero")
                    ]
                )
                sub_memory.append(
                    [
                        f'{k["reference_month"]:02d}/{k["reference_year"]:04d}: {", ".join(events)}',
                        [],
                    ]
                )
                idx += 1

        self.set_memory(f"QTD MESES RRA = {months}", sub_memory)
        self.set_memory(f"PARCELAMENTO = {installments}")
        self.set_memory(f"PARCELAS PAGAS NO MES = {installments_paid}")
        self.set_memory(
            f"FATOR = {factor} (QTD MESES RRA/PARCELAMENTO x PARCELAS PAGAS NO MES)"
        )
        self.set_memory(f"FAIXA = {self.percentage()}% (LIMITES DA FAIXA x FATOR)")


@RunCodeManager.register("gfp-mpto-irrf-13")
class IRRF13(IRRF):

    def old_base_value_query(self):
        old = super().base_value_query()
        return old.values_list("reference_year", "reference_month").first()

    def base_value_query(self):
        old_base = self.old_base_value_query()
        q_entries = Q(
            evento__numero__in=self.focuses_on,
            contracheque__servidor=self.employee,
            contracheque__pensioner=self.pensioner,
            rra_employee__isnull=True,
        )

        if self.ALL_PAYROLL and old_base:
            q_entries = (
                Q(reference_year=old_base[0], reference_month__in=[old_base[1], 13])
                & q_entries
            )
        else:
            q_entries = Q(contracheque__folha=self.reference_payroll) & q_entries

        if self.exclude_events:
            q_entries = Q(q_entries & ~Q(evento__numero__in=self.exclude_events))
        if self.only_events:
            q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))

        return Entry.objects.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )

    def discount_paid_other_payroll(self, value_field="valor"):
        year_base = self.old_base_value_query()
        total = 0
        if self.ALL_PAYROLL:
            entries = Entry.objects.filter(
                evento__genre_event=self.event.genre_event,
                contracheque__servidor=self.employee,
                contracheque__pensioner=self.pensioner,
                reference_year=year_base[0] if year_base else self.year,
                reference_month=13,
            )
            if self.entry:
                entries = entries.exclude(pk=self.entry.pk)
            # log.debug([f'{x}: {x.folha.periodo}: {x.valor}' for x in entries])
            for e in entries:
                total += e.valor if e.evento.tipo == "P" else -e.valor
        return float(abs(total))
