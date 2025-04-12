# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from memoization import cached

from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.const import CANCELADO as AFASTAMENTO_CANCELADO
from rh.gfp.models import Folha as Payroll
from rh.gfp.models import FolhaEvento as Entry
from standard.models import Configuration, RunCodeManager

log = getLogger(__name__)

BUSINESSDAYS = 30


@RunCodeManager.register("mpto-gfp-base-calculation")
class BaseCalculation(object):
    typeof = "CALCULO"
    title = "Calculo Base para MPTO"
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

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "oIds"]

    """
    MULTI_CALCULATE = True
    Usado para definir se o calculo será executado para cada elemento do get_query()
    """
    MULTI_CALCULATE = False

    JOIN_ON_MULTI = False

    FORCE_RECALCULATE_BASE = False

    RECALCULATE_BASES = 1
    # 1 - POR DEMANDA
    # 2 - NUNCA RECALCULAR
    # 3 - SEMPRE RECALCULAR (igual a FORCE_RECALCULATE_BASE = True)

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
    Indica como o get_query sera filtrado
    0: Nao filtra
    1: Filtrar apenas pelo evento
    2: Filtrar pelo evento com mesmo CID
    """
    FILTER_BY = 0

    """
     Indica se o calculo vai incidir sobre todas as verbas do periodo,
     inclusive de folhas diferentes ou se apenas da folha em questão
    """
    ALL_PAYROLL = False

    USE_CID = False

    DISCOUNT_DESC = "DESCONTOS VALOR BASE"

    MEMORY = False

    # TODO Avaliando a necessidade de ter de calcular cada evento do incide_sobre de forma individual com
    # realação a ser ou não FULL_VALUE. Caso se comprove a necessidade, as variáveis deverão ser transformadas
    # em configuração do calculo do evento
    FORCE_PAID_VALUE = []
    FORCE_FULL_VALUE = []

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
        max_deep=2,
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
        self.exclude_events = list(exclude_events)
        self.only_events = list(only_events) if only_events else []
        self.year = year or self.payroll.periodo.ano
        self.month = month or self.payroll.periodo.mes
        self.range_salary = NewDateRange.from_month(
            self.year, (self.month if self.month < 12 else 12)
        )
        self.validity = self.range_salary
        self.group_key_cache = kwargs.get("group_cache", None)
        self.pensioner = kwargs.get("pensioner", None)
        self.force_recalculate = (
            kwargs.get("force_recalculate", False) or self.FORCE_RECALCULATE_BASE
        )
        self._memory = []
        self._is_christmas_grat = False if self.month != 13 else True
        self.max_deep = max_deep - 1

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
        # log.debug(u'PARAMS[QNT]: %s TC: %s' % (self.params.get('qnt', None), self.event.tipo_calculo))
        if self.event:
            if "qnt" in self.params and self.event.tipo_calculo in [3, 5]:
                try:
                    return float(self.params["qnt"])
                except Exception:
                    return 0.0
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
            # log.debug('>>>> %s' % focuses_on)
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

        return Entry.objects.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )

    def _get_value_from_calc(self, calc, full_value=False):
        value = calc.value() if not full_value else calc.full_value()
        # log.info(f'>>>> {calc.value()} {calc.full_value()} {value}')
        return value

    def _get_value_from_entry(self, entry):
        if (
            self.FULL_VALUE and entry.evento.numero not in self.FORCE_PAID_VALUE
        ) or entry.evento.numero in self.FORCE_FULL_VALUE:
            factor = (
                (entry.correct_qnt_max / entry.correct_qnt)
                if entry.correct_qnt != 0
                else 0
            )
            value = entry.correct_valor * factor
        else:
            value = entry.correct_valor
        return float(value)

    def _get_focuses_on(self):
        fo = list(self.focuses_on)
        fo.append(self.event.numero)
        return fo

    @cached()
    def base_value(self):
        # log.debug('******************************* 1. BASE VALUE %s' % self.__class__)
        if "base_value" in self.params:
            return float(self.params["base_value"])

        if self.event and self.event.base_value_at(self.range_salary.first):
            return float(self.event.base_value_at(self.range_salary.first))

        total = 0.00
        for fe in self.base_value_query():
            has_calc = fe.evento.automated and fe.classcode
            other_reference = (
                fe.reference_year != self.year or fe.reference_month != self.month
            )
            memory_calc = []
            # log.debug(' CALCULATING %s > %s: %s and %s and (%s or %s or %s)' % (self.event.numero,
            #                                                                     fe.evento.numero,
            #                                                                     fe.evento.automated,
            #                                                                     fe.classcode,
            #                                                                     fe.reference_year != self.year,
            #                                                                     fe.reference_month != self.month,
            #                                                                     self.force_recalculate))
            if (
                has_calc
                and self.max_deep > 0
                and (
                    self.RECALCULATE_BASES == 3
                    or (self.RECALCULATE_BASES == 1 and other_reference)
                    or self.force_recalculate
                )
            ):
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
                    only_events=(
                        self._get_focuses_on()
                        if not self.only_events
                        else self.only_events
                    ),
                    group_cache=self.group_key_cache,
                    entry=fe,
                    pensioner=fe.contracheque.pensioner,
                    force_recalculate=self.force_recalculate,
                    cid=fe.cid,
                    max_deep=self.max_deep,
                )
                # value = calc.value() if not self.FULL_VALUE else calc.full_value()
                value = self._get_value_from_calc(calc, self.FULL_VALUE)
                value = value if fe.evento.tipo == "P" else -value
                memory_calc = getattr(calc, "_memory", [])
                # log.debug(f'RECALC > {value}')
            else:
                value = self._get_value_from_entry(fe)
                value = value if fe.evento.tipo == "P" else -value
                # log.debug(f'NO RECALC > {value}')
            diff_payroll = f" - {fe.folha}" if fe.folha != self.payroll else ""
            self.set_memory(
                f'VALOR BASE = {total:0.2f} {"+" if value > 0 else "-"} {abs(value):0.2f} = {(total + value):0.2f} ({fe.evento.numero}{diff_payroll})',
                memory_calc,
            )
            # log.debug('>>>> %s >>>> %s : %s + %s = %s' %
            #           (self.event.numero if self.event else 'XXX-XX', fe.evento.numero, total, value, total + value))
            total += value
        base_discounts = self.base_discounts()
        base_value = total - base_discounts
        if base_discounts:
            self.set_memory(
                f"VALOR BASE = {total:0.2f} - {base_discounts:0.2f}({self.DISCOUNT_DESC}) = {base_value:0.2f}"
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
        base = self.base_value()
        pct = self.percentage()
        factor = self.factor_quantity()
        discount_paid = self.discount_paid_other_payroll()

        value = base * (float(pct) / 100.00)
        self.set_memory(f"VALOR = {base:0.2f} x {pct}% = {value:0.2f}")
        if factor != 1:
            ivalue = value
            value *= factor
            self.set_memory(f"VALOR = {ivalue:0.2f} x {factor}(FATOR) = {value:0.2f}")
        if discount_paid:
            value -= discount_paid
            self.set_memory(
                f"VALOR = {value:0.2f} - {discount_paid}(VALOR JÁ APURADO) = {value:0.2f}"
            )
        if value:
            value = min(value, self.ceiling)
            if value == self.ceiling:
                self.set_memory(
                    f"VALOR = {value:0.2f}(TETO) ( VALOR > TETO {self.ceiling:0.2f}"
                )
            value = max(value, self.floor)
            if value == self.floor:
                self.set_memory(
                    f"VALOR = {value:0.2f}(PISO) ( VALOR < PISO {self.floor:0.2f}"
                )
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

    def _filter_repeateds(self):
        q_entries = self.employee.entries.filter(
            evento=self.event, contracheque__pensioner=None
        )
        if self.entry:
            q_entries = q_entries.exclude(pk=self.entry.pk)
        if self.FILTER_QUERY == 0:
            q_entries = self.employee.entries.none()
        elif self.FILTER_QUERY == 1:
            q_entries = q_entries.filter(folha=self.payroll)
        elif self.FILTER_QUERY == 2:
            q_entries = q_entries.filter(
                reference_month=self.month, reference_year=self.year
            )
        return q_entries

    def _exclude_repeated_cids(self):
        q_entries = self._filter_repeateds()
        cids = [
            (fe.cid if self.USE_CID else (fe.oIds[0] if fe.oIds else None))
            for fe in q_entries
        ]
        # log.debug('CIDS: %s' % cids)
        return cids

    def get_query(self):
        if self.FILTER_BY == 1:
            if self._filter_repeateds().exists():
                return []
        elif self.FILTER_BY == 2:
            return [
                obj
                for obj in self._get_query()
                if getattr(obj, "pk", obj) not in self._exclude_repeated_cids()
            ]
        return self._get_query()

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
        }

        try:
            self.validate()
            self.configure()
            # log.debug('CALCULATE SINGLE %s (%s)' % (self.validity, self.params))
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
                        2,
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
                }
            )
            # log.debug('CALC VALUES: %s' % obj)
        except self.CalculationNotApplicable:
            # log.info('Calculo %s nao aplicavel ao servidor %s' % (self.title, self.employee))
            obj["validate"]["message"] = "Calculo %s nao aplicavel ao servidor %s" % (
                self.title,
                self.employee,
            )
        except Exception as e:
            log.info(f">>>>>>>>>>>>>>>>>>>>>> {self.__class__.__name__}")
            log.info(f">>>>>>>>>>>>>>>>>>>>>> {self.employee}")
            log.exception(e)
            obj["validate"]["message"] = "Erro no cálculo! %s" % e

        return obj

    def calculate_multi(self):
        calcs = []
        try:
            self.validate()
            self.configure()
        except self.CalculationNotApplicable:
            # log.info('Calculo %s nao aplicavel ao servidor %s' % (self.title, self.employee))
            pass
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

    def set_memory(self, value, sub_calc=[]):
        if self.MEMORY:
            self._memory.append([value, sub_calc])


class WorkDaysCalculation(BaseCalculation):
    """
    Calculo que utiliza a quantidade de dias de efetivo exercicio no mês de
    referencia da folha para calcular o 'qnt'
    """

    BASE_BUSINESSDAYS = False
    IGNORE_DEPARTURE = False
    EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {}
    EXCLUDE_BY_JOB = ["AC"]

    @property
    @cached()
    def base_days(self):
        return BUSINESSDAYS if self.BASE_BUSINESSDAYS else self.range_salary.days

    @cached()
    def get_possessions(self):
        possessions = (
            self.employee.posses.exclude(Q(data_exercicio__gt=self.range_salary.last))
            .filter(
                Q(desligamento=None)
                | Q(desligamento__data_desligamento__gte=self.range_salary.first)
            )
            .with_office_valid_in(self.range_salary)
            .distinct()
            .order_by("-data_exercicio")
        )

        # log.debug('VAI A LISTA: %s' % possessions)

        return possessions  # .exclude(quadro__cargo__tipo_lei_cargo__in=self.EXCLUDE_BY_JOB)

    def _exclude_ranges_for_range_salary(self, range_salary=None):
        if not range_salary:
            range_salary = self.range_salary

        range_unpaid_absences = NewDateRange()

        # log.debug(f' >>>> CALCULANDO RSF IN ERFRS> {range_unpaid_absences} | {self.IGNORE_DEPARTURE} | {range_salary}')

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
            # log.debug(range_unpaid_absences)
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
            # log.debug(range_unpaid_absences)
        # log.debug(u'SFE ERANGES: %s' % range_unpaid_absences)

        return range_unpaid_absences

    def _intersect_ranges_for_range_salary(self):
        # print(type(self.range_salary))
        # print(type(self.validity))
        return self.range_salary.intersect(self.validity)

    def range_salary_for(
        self, possession=None, range_salary=None, get_possessions_from13=False
    ):
        # log.debug(u'SFE %s RSF 1: %s' % (self.__class__.__name__, possession))
        # log.debug(f' >>>> CALCULANDO RSF > {possession} | {range_salary} | {get_possessions_from13}')
        # print(range_salary)
        if not range_salary:
            range_salary = self._intersect_ranges_for_range_salary()
        ranges_ = NewDateRange()
        # print(range_salary)

        if range_salary.days == 0:
            return ranges_
        # log.debug(u'>>>> CALCULANDO RSF SFE %s RSF 2 %s' % (self.__class__.__name__, range_salary))
        get_possessions = (
            self.get_possessions()
            if not get_possessions_from13
            else self.get_possessions_13()
        )
        if not possession:
            for possession in get_possessions:
                ranges_ += NewDateRange(
                    possession.financial_effect_date_start,
                    (
                        (possession.financial_effect_date_end - relativedelta(days=1))
                        if possession.financial_effect_date_end
                        else None
                    ),
                )
            # possession_request = self.get_possessions().filter(requestmove__isnull=True).first()
        else:
            ranges_ = NewDateRange(
                possession.financial_effect_date_start,
                (
                    (possession.financial_effect_date_end - relativedelta(days=1))
                    if possession.financial_effect_date_end
                    else None
                ),
            )
            # possession_request = possession if possession.instancia_modelo == 'requestmove' else None

        # if possession_request:
        #     ranges_requested_ = NewDateRange()
        #     for req in possession_request.requisicao.exclude(
        #         Q(data_inicio__gt=range_salary.last) |
        #         (
        #             ~Q(data_fim=None) &
        #             Q(data_fim__lt=range_salary.first)
        #         )
        #     ):
        #         ranges_requested_ += NewDateRange(req.data_inicio, req.data_fim)
        #     ranges_ = ranges_.intersect(ranges_requested_)
        # print(f'TOME OS RANGES {ranges_}')
        # print(f'TOME TB O RANGE SALARY {range_salary}')
        ranges_ = ranges_.intersect(
            range_salary
        ) - self._exclude_ranges_for_range_salary(range_salary=range_salary)
        # log.debug(u'SFE %s RSF 4 %s' % (self.__class__.__name__, range_salary))

        return ranges_

        # return (ranges_ - range_unpaid_absences) if range_unpaid_absences.days > 0 else ranges_

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
            .order_by("-data_exercicio")
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
        # log.debug('   ******CALCULANDO QTD 13º SALARIO --------------------------')
        return self.range_salary_for(
            range_salary=range_year, get_possessions_from13=True
        )

    @cached()
    def get_possessions_13(self):
        # print('TO NO get_possessions de 13')
        range_year = NewDateRange(
            datetime(self.year, 1, 1), datetime(self.year, 12, 31)
        )
        possessions = (
            self.employee.posses.exclude(
                Q(data_exercicio__gt=range_year.last)
                | (
                    ~Q(desligamento=None)
                    & Q(desligamento__data_desligamento__lte=range_year.first)
                )
            )
            .with_office_valid_in(self.range_salary)
            .distinct()
            .order_by("-data_exercicio")
        )
        # log.debug(self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB)
        print(self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB)
        for k in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.keys():
            possessions = possessions.exclude(
                servidor__tipo=k,
                quadro__cargo__tipo_lei_cargo__in=self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB[
                    k
                ],
            )

        # log.debug('AdvanceChristmasGratification: %s' % possessions)
        print(possessions)
        return possessions  # .exclude(quadro__cargo__tipo_lei_cargo__in=self.EXCLUDE_BY_JOB)


class PercentageCalculation(BaseCalculation):
    def percentage(self):
        return 0.00
