# -*- coding: utf-8 -*-
from datetime import datetime
from rh.models import DeclaracaoAtividade, MovimentacaoRequisicao

from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from memoization import cached

from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.const import CANCELADO as AFASTAMENTO_CANCELADO
from rh.gfp.models import (
    Folha as Payroll,
    FolhaEvento as Entry,
    EstruturaTabelaSalarial,
)
from standard.models import Configuration, RunCodeManager

log = getLogger(__name__)

BUSINESSDAYS = 30

EMPLOYEE_TYPES = [
    "EFE",
    "ECM",
    "EFC",
    "MBR",
    "MEL",
    "MCM",
    "MEC",
    "MBR2",
    "MEL2",
    "MCM2",
    "MEC2",
    "CMS",
]
REQUESTED_TYPES = []


@RunCodeManager.register("mpmt-gfp-base-calculation")
class BaseCalculation(object):
    typeof = "CALCULO"
    title = "Calculo Base"
    description = "Este calculo pode ser usado de forma genérica para calculos simples"

    class ErroCalculation(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Erro ao calcular evento...")
            )

    class CalculationNotApplicable(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Cálculo não aplicável ao servidor...")
            )

    # Parametros que poderão ser usados como @params do calculo
    PARAMS_ = ["info", "oIds", "qnt"]

    """
    MULTI_CALCULATE = True
    Usado para definir se o calculo será executado para cada elemento do get_query()
    """
    MULTI_CALCULATE = False

    JOIN_ON_MULTI = False

    RECALCULATE_BASES = 1
    # 1 - POR DEMANDA
    # 2 - NUNCA RECALCULAR
    # 3 - SEMPRE RECALCULAR (igual a RECALCULATE_BASES = 3)

    EVALUATE_ON_REFERENCE_PAYROLL = False

    FULL_VALUE = False

    CAN_UPDATE_CID = False

    """
    Indica se o get_query sera filtrado pela existencia de algum lancamento do mesmo evento
    0: Nao filtra
    1: Filtrar repetidos apenas dentro da mesma folha
    2: Filtrar repetidos na mesma referencia
    3: Filtrar ja existente, independente de quando ocorreu o pagamento
    """
    FILTER_QUERY = 0

    """
     Indica se o calculo vai incidir sobre todas as verbas do periodo,
     inclusive de folhas diferentes ou se apenas da folha em questão
    """
    ALL_PAYROLL = False

    USE_CID = False

    def __init__(
        self,
        employee,
        payroll,
        event=None,
        entry=None,
        exclude_events=[],
        only_events=[],
        year=None,
        month=None,
        memory=False,
        level=0,
        **kwargs,
    ):
        """
        Inicializador do calculo, recebe o servidor, folha a ser calculada e o evento que possui o calculo automático.
        """
        # log.debug('>>> %s with (%s, %s, %s, %s, %s, %s, %s, %s, %s)<<<' % (self.__class__, employee, payroll, event,
        #     entry, exclude_events, only_events, year, month, kwargs))
        self.cfg = Configuration.get_or_create("gfp")
        self.payroll = payroll
        self.employee = employee
        self.event = event
        self.entry = entry
        self.exclude_events = list(exclude_events or [])
        self.only_events = list(only_events or [])
        self.year = year or self.payroll.periodo.ano
        self.month = month or self.payroll.periodo.mes
        self.range_salary = NewDateRange.from_month(
            self.year, (self.month if self.month < 12 else 12)
        )
        self.validity = self.range_salary
        self.group_key_cache = kwargs.get("group_cache", None)
        self.pensioner = kwargs.get("pensioner", None)
        self.level = level + 1
        self.source_event = kwargs.get("source_event", None)
        self._memory = []
        self._is_christmas_grat = False if self.month != 13 else True

        # Carregando apenas os params que poder ser passados para o calculo. Definidos em @PARAMS_
        # log.debug('PARAMS FOR B: %s - %s' % (self.event, kwargs['params'] if 'params' in kwargs else []))
        self.params = {}
        if "params" in kwargs:
            for p in kwargs["params"]:
                if p in self.PARAMS_:
                    self.params[p] = kwargs["params"][p]
        # log.debug('PARAMS FOR A: %s - %s' % (self.event, kwargs['params'] if 'params' in kwargs else []))

        # REMOVING DATA BUG
        if "oIds" in self.params and self.params["oIds"] == [""]:
            self.params.pop("oIds")

        self.configure()
        # log.debug('CALC FOR %s - %s %s' % (self.event.numero, self.entry.pk if self.entry else 'XXXXXX', self.params))

    def configure(self):
        pass

    @property
    @cached()
    def range_base(self):
        return self.range_salary.intersect(
            NewDateRange(self.employee.data_exercicio, self.employee.last_day_worked)
        )

    @property
    @cached()
    def range_calc(self):
        return self.range_base

    @property
    def reference_payroll(self):
        # log.debug(self.references)
        if self.EVALUATE_ON_REFERENCE_PAYROLL and (
            self.references[0] != self.payroll.periodo.ano
            or self.references[1] != self.payroll.periodo.mes
        ):
            # Tentar modificar a folha para a folha do período de referência do calculo
            _payroll = Payroll.objects.filter(
                tipo_folha=self.payroll.tipo_folha,
                periodo__ano=self.references[0],
                periodo__mes=self.references[1],
            ).first()
            # log.debug(_payroll)
            if _payroll:
                return _payroll
        return self.payroll

    @property
    def identification_payroll(self):
        return "%04d%02d" % (
            self.range_salary.first.year,
            self.range_salary.first.month,
        )

    @property
    @cached()
    def employee_types(self):
        possessions = self.employee.get_posses_ativas(
            self.range_salary.first, self.range_salary.last
        )
        by_joposition = [
            mp.quadro.cargo.tipo_lei_cargo for mp in possessions if mp.quadro
        ]
        if possessions.filter(requestmove__isnull=False):
            by_joposition.append("AC")
        return by_joposition

    @cached()
    def maximum_quantity(self):
        if self.event and self.event.max_quantity_at(self.range_salary.first):
            return float(self.event.max_quantity_at(self.range_salary.first))
        return 0.00

    @cached()
    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)
            if self.event.quantity_at(self.range_salary.first) is not None:
                return float(self.event.quantity_at(self.range_salary.first))
        return self.maximum_quantity()

    @cached()
    def factor_quantity(self):
        factor = 1.0
        try:
            factor = float(self.quantity()) / float(self.maximum_quantity())
        except ZeroDivisionError:
            factor = 1.0
        except Exception as e:
            log.exception(e)

        return factor

    @cached()
    def percentage(self):
        pct = 100.0
        if self.event:
            if self.params.get("pct") and self.event.tipo_calculo in [1, 5]:
                pct = float(self.params["pct"])
            if self.event.percentage_at(self.range_salary.first):
                pct = float(self.event.percentage_at(self.range_salary.first))
        # log.debug(u'PORCENTAGEM de BaseCalculo: %s' % pct)
        return float(pct)

    def installment(self):
        installment = 0
        if self.event and self.event.lancamento == "T":
            installment = 1
            if self.params.get("installment"):
                installment = int(self.params["installment"])

        return installment

    def installments_paid(self):
        installments_paid = 0
        if self.event and self.event.lancamento == "T":
            installments_paid = 1
            if self.params.get("installments_paid"):
                installments_paid = int(self.params["installments_paid"])

        return installments_paid

    def total_installment(self):
        total_installment = 0
        if self.event and self.event.lancamento == "T":
            total_installment = 1
            if self.params.get("total_installment"):
                total_installment = int(self.params["total_installment"])

        return total_installment

    # @cached()
    def base_socialsecurity(self, total=False):
        """
        Este calculo deve ser sobrescrito para todo calculo que
        se deseja saber a base previdenciária utilizada pelo calculo
        """
        # log.info(u'BP de BaseCalculo')
        return self.value()

    @cached()
    def base_discounts(self):
        return 0.0

    @property
    # @cached()
    def focuses_on(self):
        focuses_on = []
        if self.event:
            focuses_on = [
                e.numero for e in self.event.focuses_on_at(self.range_salary.first)
            ]
        if self.only_events:
            focuses_on = [
                event_number
                for event_number in focuses_on
                if event_number in self.only_events
                and event_number not in self.exclude_events
            ]
        return focuses_on

    def base_value_query(self):
        q_entries = Q(
            evento__numero__in=self.focuses_on,
            contracheque__servidor=self.employee,
            contracheque__pensioner=self.pensioner,
        )

        if self.ALL_PAYROLL:
            q_entries = (
                Q(contracheque__folha__periodo=self.reference_payroll.periodo)
                & q_entries
            )
        else:
            q_entries = Q(contracheque__folha=self.reference_payroll) & q_entries

        if self.exclude_events:
            q_entries = Q(q_entries & ~Q(evento__numero__in=self.exclude_events))
        if self.only_events:
            q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))
        query = Entry.objects.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )
        if self.entry:
            query = query.exclude(pk=self.entry.pk)
        return query

    def _factor_calc(self, calc):
        range_i = calc.range_calc.intersect(self.range_calc)
        log.info(
            f">>>> {range_i.days / self.range_salary.days} {calc.range_calc}I{self.range_calc}={range_i}"
        )
        return range_i.days / self.range_salary.days

    def _get_value_from_calc(self, calc, full_value=False):
        value = calc.value() if not full_value else calc.full_value()
        # log.info(f'>>>> {calc.value()} {calc.full_value()} {value}')
        return value

    def _get_value_from_entry(self, entry):
        return float(
            entry.correct_valor if self.FULL_VALUE is False else entry.valor_base
        )

    def _value_calc_normatized(self, calc, full_value=False):
        log.info("_value_calc_normatized")
        # reparar se haverá alteração nos cálculos da linha cometada abaixo - removendo o factor_calc
        # return self._get_value_from_calc(calc, full_value=full_value) * self._factor_calc(calc)
        return self._get_value_from_calc(calc, full_value=full_value)

    def _get_focuses_on(self):
        return list(self.focuses_on).append(self.event.numero)

    @cached()
    def base_value(self):
        log.debug("******************************* 1. BASE VALUE %s" % self.__class__)
        if "base_value" in self.params:
            return float(self.params["base_value"])

        if self.event and self.event.base_value_at(self.range_salary.first):
            return float(self.event.base_value_at(self.range_salary.first))

        total = 0.00

        log.debug(
            f">>>> L{self.level} INI CALCULATING {self.event} {self.RECALCULATE_BASES} {self.level}"
        )
        for fe in self.base_value_query():
            has_calc = fe.evento.automated and fe.classcode
            other_reference = (
                fe.reference_year != self.year or fe.reference_month != self.month
            )
            recalculate = self.RECALCULATE_BASES == 3 or (
                self.RECALCULATE_BASES == 1 and other_reference
            )
            # log.debug(' CALCULATING %s > %s: %s and %s and (%s or %s or %s)' % (self.event.numero,
            #                                                                     fe.evento.numero,
            #                                                                     fe.evento.automated,
            #                                                                     fe.classcode,
            #                                                                     fe.reference_year != self.year,
            #                                                                     fe.reference_month != self.month,
            #                                                                     self.level))
            if (
                has_calc
                and self.level <= 2
                and self.source_event != fe.evento
                and recalculate
            ):
                log.debug(
                    f">>>> L{self.level} CALCULATING {self.event} > {fe.evento} >>>> {self.focuses_on}"
                )
                params = {
                    "pct": fe.correct_pct,
                    "qnt": fe.correct_qnt,
                    "info": fe.info,  # 'oIds': fe.oIds,
                    "patronal": fe.correct_employer_contribution,
                    "valor_base": fe.correct_base_value,
                }
                params.update(fe.vars)
                calc = fe.classcode.cls(
                    fe.servidor,
                    fe.folha,
                    fe.evento,
                    year=self.references[0],
                    month=self.references[1],
                    params=params,
                    only_events=self._get_focuses_on(),
                    group_cache=self.group_key_cache,
                    entry=fe,
                    pensioner=fe.contracheque.pensioner,
                    level=self.level,  # Informando o nivel que está chamando o calculo
                    cid=fe.cid,
                )
                value = self._value_calc_normatized(calc, full_value=self.FULL_VALUE)
                value = value if fe.evento.tipo == "P" else -value
                # log.debug(f'RECALC > {value}')
            else:
                log.debug(
                    f">>>> L{self.level} NO CALCULATING {self.event} > {fe.evento}"
                )
                value = self._get_value_from_entry(fe)
                value = value if fe.evento.tipo == "P" else -value
                # log.debug(f'NO RECALC > {value}')

            self._memory.append(
                f"VALOR BASE = {total} + {value} = {total + value} ({fe.evento.numero})"
            )
            log.debug(
                ">>>> %s >>>> %s : %s + %s = %s"
                % (
                    self.event.numero if self.event else "XXX-XX",
                    fe.evento.numero,
                    total,
                    value,
                    total + value,
                )
            )
            total += value
        base_discounts = self.base_discounts()
        base_value = total - base_discounts
        if base_discounts:
            self._memory.append(
                f"VALOR BASE = {total} - {base_discounts} = {base_value} (DESCONTOS VALOR BASE)"
            )
        base_value = (
            base_value
            if not (self.event and self.event.calculo_invertido)
            else -base_value
        )
        return min(base_value, self.ceiling_base_value)

    @property
    @cached()
    def ceiling(self):
        return (
            float(self.event.ceiling_at(self.range_salary.first))
            if self.event and self.event.ceiling_at(self.range_salary.first)
            else 9999999.99
        )

    @property
    def ceiling_base_value(self):
        return 9999999.99

    @property
    @cached()
    def floor(self):
        return (
            float(self.event.floor_at(self.range_salary.first))
            if self.event and self.event.floor_at(self.range_salary.first)
            else 0.00
        )

    def discount_paid_other_payroll(self, value_field="correct_valor"):
        if self.ALL_PAYROLL:
            entries = Entry.objects.filter(
                evento=self.event,
                contracheque__servidor=self.employee,
                contracheque__pensioner=self.pensioner,
                contracheque__folha__periodo=self.reference_payroll.periodo,
            )
            if self.entry:
                entries = entries.exclude(pk=self.entry.pk)
            return float(entries.aggregate(total=Sum(value_field)).get("total") or 0)
        return 0

    @cached()
    def value(self):
        value = (
            self.base_value()
            * (float(self.percentage()) / 100.00)
            * self.factor_quantity()
        )
        value -= self.discount_paid_other_payroll()
        if value:
            value = min(value, self.ceiling)
            value = max(value, self.floor)
        return value

    def full_value(self):
        try:
            return self.value() / self.factor_quantity()
        except ZeroDivisionError:
            return 0.0

    @cached()
    def employer_value(self):
        if "patronal" in self.params:
            return float(self.params["patronal"])
        return 0.0

    @cached()
    def event_information(self):
        if "info" in self.params:
            return self.params["info"]
        return ""

    def validate(self):
        self.validate_not_paycheck_pension()

    def validate_not_paycheck_pension(self):
        if self.pensioner:
            raise self.CalculationNotApplicable(
                "Cálculo não pode ser aplicado a contracheque de pensionistas!"
            )

    def validate_if_employee_not_in_slug_extra(self):
        if not self.get_query():
            txt = f"O servidor {self.employee} não possui pagamento configurado para a TAG {self.SLUG_EXTRA_PAYMENT_FOR_AID}"
            raise self.CalculationNotApplicable(txt)

    def callback(self, **kargs):
        pass
        # log.debug('CALLBACK for %s' % self.__class__.__name__)

    @property
    def oIds(self):
        return [(obj.pk if hasattr(obj, "pk") else obj) for obj in self.get_query()]

    @property
    def cid(self):
        return self.oIds[0]

    def vars(self):
        """
        Por padrão usa-se {oIds: [value1, value2, ...]}
        """
        return {"oIds": self.oIds}

    def _get_query(self):
        return []

    def _exclude_repeated_cids(self):
        q_entries = self.employee.entries.filter(evento=self.event)
        if self.entry:
            q_entries = q_entries.exclude(pk=self.entry.pk)
        if self.FILTER_QUERY == 0:
            q_entries = []
        elif self.FILTER_QUERY == 1:
            q_entries = q_entries.filter(folha=self.payroll)
        elif self.FILTER_QUERY == 2:
            q_entries = q_entries.filter(
                reference_month=self.month, reference_year=self.year
            )
        cids = [
            (fe.cid if self.USE_CID else (fe.oIds[0] if fe.oIds else None))
            for fe in q_entries
        ]
        return cids

    def get_query(self):
        return [
            obj
            for obj in self._get_query()
            if getattr(obj, "pk", obj) not in self._exclude_repeated_cids()
        ]

    def choices(self):
        return [
            (obj.pk if hasattr(obj, "pk") else obj, self.unicode_for_obj(obj))
            for obj in self.get_query()
        ]

    @property
    @cached()
    def object(self):
        if len(self.get_query()) == 1:
            return self.get_query()[0]
        return None

    def get_params_for_obj(self, obj):
        return {"oIds": [obj.pk if hasattr(obj, "pk") else obj]}

    def unicode_for_obj(self, obj):
        return str(obj)

    def range_for_obj(self, obj):
        return NewDateRange()

    @property
    def references(self):
        return (self.year, self.month)

    def calculate_single(self):
        # log.debug('CALCULAR of %s [%s]' % (self.__class__.__name__, self.params))
        """
        Metodo responsável por realizar o calculo.
        """
        obj = {
            "qnt": 0,
            "qnt_max": 0,
            "pct": 0,
            "valor_base": 0,
            "valor": 0,
            "base_previdencia": 0,
            "patronal": 0,
            "info": "",
            "vars": {},
            "callback": self.callback,
            "validate": {"message": ""},
            "oIds": [],
            "choices": [],
            "references": self.references,
            "automated": True,
            "parcela": 0,
            "installments_paid": 1,
            "prazo": 0,
            "memory": [],
            "range": self.range_calc,
        }

        try:
            self.validate()
            self.configure()
            obj.update(
                {
                    "qnt": self.quantity(),
                    "qnt_max": round(self.maximum_quantity(), 2),
                    "pct": round(
                        (
                            self.percentage()
                            if self.event and self.event.tipo_calculo in [1, 5]
                            else 0.0
                        ),
                        4,
                    ),
                    "valor_base": round(self.base_value(), 2),
                    "valor": round(self.value(), 2),
                    "base_previdencia": round(self.base_socialsecurity(), 2),
                    "patronal": round(self.employer_value(), 2),
                    "info": self.event_information(),
                    "vars": self.vars(),
                    "oIds": self.oIds,
                    "choices": self.choices(),
                    "parcela": self.installment(),
                    "installments_paid": self.installments_paid(),
                    "prazo": self.total_installment(),
                    "memory": self._memory,
                    "range": self.range_calc,
                }
            )
            # log.debug('CALC VALUES: %s' % obj)
        except self.CalculationNotApplicable:
            log.info(
                "Calculo %s nao aplicavel ao servidor %s" % (self.title, self.employee)
            )
            obj["validate"]["message"] = "Calculo %s nao aplicavel ao servidor %s" % (
                self.title,
                self.employee,
            )
        except Exception as e:
            log.exception(e)
            obj["validate"]["message"] = "Erro no cálculo! %s" % e

        return obj

    def calculate_multi(self):
        calcs = []
        try:
            self.validate()
            self.configure()
        except self.CalculationNotApplicable:
            log.info(
                "Calculo %s nao aplicavel ao servidor %s" % (self.title, self.employee)
            )
        except Exception as e:
            log.exception(e)
        else:
            for obj in self.get_query():
                params = self.params.copy()
                params.update(self.get_params_for_obj(obj))
                # log.debug('CALCULATE MULTI PARAMS %s' % params)
                calcs.append(
                    self.__class__(
                        self.employee,
                        self.payroll,
                        self.event,
                        params=params,
                        group_cache=self.group_key_cache,
                    ).calculate_single()
                )

        return calcs

    def calculate(self):

        result = {
            "qnt": 0,
            "qnt_max": 0,
            "pct": 0,
            "valor_base": 0,
            "valor": 0,
            "base_previdencia": 0,
            "patronal": 0,
            "info": "",
            "vars": {},
            "callback": self.callback,
            "validate": {"message": ""},
            "oIds": [],
            "choices": [],
            "references": self.references,
            "parcela": 0,
            "installments_paid": 1,
            "prazo": 0,
            "memory": [],
            "range": self.range_calc,
        }
        try:
            self.validate()
            # self.configure()
        except Exception as e:
            result["validate"]["message"] = str(e)
            return result

        if not self.MULTI_CALCULATE or len(self.get_query()) == 1:
            return self.calculate_single()
        else:
            if not self.JOIN_ON_MULTI and len(self.get_query()) > 1:
                result["choices"] = self.choices()
                return result
            else:
                for calc in self.calculate_multi():
                    result["qnt"] += calc["qnt"]
                    result["valor"] += calc["valor"]
                    result["base_previdencia"] += calc["base_previdencia"]
                    result["patronal"] += calc["patronal"]
                    result["oIds"] += calc["oIds"]
                    result["valor_base"] += calc["valor_base"]

                result["valor_base"] = (
                    (result["valor_base"] / float(len(self.calculate_multi())))
                    if len(self.calculate_multi()) > 0
                    else 0.00
                )

                return result

    # ****************** DEPRECATED METHODS ****************************
    def calcular(self):
        return self.calculate()

    def valor(self):
        return self.value()

    def valor_base(self):
        return self.base_value()


class WorkDaysCalculation(BaseCalculation):
    """
    Calculo que utiliza a quantidade de dias de efetivo exercicio no mês de
    referencia da folha para calcular o 'qnt'
    """

    BASE_BUSINESSDAYS = False
    IGNORE_DEPARTURE = False
    IGNORE_DEPARTURE_REMUNERATE_FILTER = True
    EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {}
    FILTER_BY_DEPARTURES = []

    @property
    @cached()
    def base_days(self):
        return BUSINESSDAYS if self.BASE_BUSINESSDAYS else self.range_salary.days

    @cached()
    def get_possessions(self):
        possessions = (
            self.employee.posses.exclude(
                Q(financial_effect_date_start__gt=self.range_salary.last)
            )
            .filter(
                Q(financial_effect_date_end=None)
                | Q(financial_effect_date_end__gte=self.range_salary.first)
            )
            .order_by("-financial_effect_date_start")
        )

        if self.employee.type_by_possession not in ("SAP", "MAP", "MAP2", "EXT", "BFP"):
            possessions = possessions.with_office_valid_in(self.range_salary)

        return possessions.distinct()

    def _exclude_ranges_for_range_salary(self, range_salary=None):
        if not range_salary:
            range_salary = self.range_salary

        range_unpaid_absences = NewDateRange()

        if self.IGNORE_DEPARTURE is False:
            for mc in AfastamentoOutroOrgao.objects.filter(
                servidor=self.employee
            ).exclude(
                Q(data_inicio__gt=range_salary.last)
                | Q(onus=1)
                | Q(transito_pela_folha=True)
                | Q(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(mc.data_inicio, mc.data_fim)
            for absence in (
                BaseLicencaAfastamento.objects.filter(
                    remunerado=False, servidor=self.employee
                )
                .exclude(
                    Q(data_fim__lt=range_salary.first)
                    | Q(data_inicio__gt=range_salary.last)
                )
                .exclude(~Q(afastamento__afastamentooutroorgao=None))
                .exclude(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(
                    absence.data_inicio, absence.data_fim
                )

        return range_unpaid_absences

    def _intersect_ranges_for_range_salary(self):
        return self.range_salary.intersect(self.validity)

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

        ranges_ = ranges_.intersect(
            range_salary
        ) - self._exclude_ranges_for_range_salary(range_salary=range_salary)
        return ranges_

    def get_possessions_by_type(self, types=[]):
        """
        Retorna as posses de efetivo que o servidor tinha no mes da referencia da folha,
        pois pode ser que o servidor começou o mês com um cargo e depois tomou posse
        em outro sendo exonerado do primeiro
        """
        if not isinstance(types, list):
            types = [
                types,
            ]
        possessions = (
            self.get_possessions()
            .filter(quadro__cargo__tipo_lei_cargo__in=types)
            .order_by("-financial_effect_date_start")
        )

        return possessions

    def quantity(self):
        return (
            self.range_salary_for().business_days
            if self.BASE_BUSINESSDAYS
            else self.range_salary_for().days
        )

    def maximum_quantity(self):
        return (
            self.base_days
            if not self._is_christmas_grat
            else self.event.max_quantity_at(self.range_salary.first)
        )

    @property
    @cached()
    def range_13salary(self):
        # vai pro base salary
        range_year = NewDateRange(
            datetime(self.year, 1, 1), datetime(self.year, 12, 31)
        )
        log.debug("   ******CALCULANDO QTD 13º SALARIO --------------------------")
        return self.range_salary_for(
            range_salary=range_year, get_possessions_from13=True
        )

    @cached()
    def get_possessions_13(self):
        log.debug("TO NO get_possessions de 13")
        range_year = NewDateRange(
            datetime(self.year, 1, 1), datetime(self.year, 12, 31)
        )
        possessions = self.employee.posses.exclude(
            Q(financial_effect_date_start__gt=range_year.last)
            | (
                ~Q(financial_effect_date_end=None)
                & Q(financial_effect_date_end__lte=range_year.first)
            )
        ).order_by("-financial_effect_date_start")
        log.debug(self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB)
        for k in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.keys():
            possessions = possessions.exclude(
                servidor__tipo=k,
                quadro__cargo__tipo_lei_cargo__in=self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB[
                    k
                ],
            )

        return possessions

    @property
    @cached()
    def range_calc(self):
        return self.range_salary_for()

    def validate_type_by_possession(self, types_by_possession):
        if self.employee.type_by_possession not in types_by_possession:
            raise self.CalculationNotApplicable(
                f"Essa verba é somente para servidor com type_by_possession {types_by_possession}!"
            )

    def validate_possessions(self):
        if not self.get_possessions():
            raise self.CalculationNotApplicable(
                f"O Servidor {self.employee} não tem posses ativas no período."
            )


class PercentageCalculation(BaseCalculation):
    def percentage(self):
        return 0.00
