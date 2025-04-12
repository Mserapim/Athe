# -*- coding: utf-8 -*-

from django.db.models import Max, Q

from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import BaseCalculation
from rh.gfp.models import IRRF as IRRFModel
from rh.gfp.models import RRA, IRRFFaixa, RRAServidorFolhaTipo
from rh.models import Dependencia, ProcessSuspension
from standard.models import RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("gfp-mpto-irrf")
class IRRF(BaseCalculation):
    title = "Calculo de imposto retido na fonte"

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
        return Dependencia.objects.filter(
            Q(
                tipo=1,
                suspenso=False,
                data_inicio__lte=self.range_salary.last,
                dependente__responsavel=self.employee.pessoa_fisica,
            )
            & (Q(data_fim=None) | Q(data_fim__gte=self.range_salary.last))
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

    @cache_return
    def value(self):
        if (
            self.employee.molestia
            and self.employee.molestia.data_laudo < self.range_salary.last
        ):
            return 0.00
        base_1 = self.base_value() * self.percentage() / 100.0
        return base_1 - self.range().get("discount", 0.00)

    def base_socialsecurity(self):
        return 0


@RunCodeManager.register("gfp-mpto-irrf-rra")
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
