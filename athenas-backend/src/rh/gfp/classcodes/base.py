# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum

from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.const import CANCELADO as AFASTAMENTO_CANCELADO
from rh.gfp.models import Folha as Payroll
from rh.gfp.models import FolhaEvento as Entry
from rh.gfp.models import Evento as Event
from standard.models import Configuration, RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("gfp-base-calculation")
class BaseCalculation(object):
    """[summary]

    Arguments:
        object {[type]} -- [description]

    Raises:
        self.CalculationNotApplicable -- [description]

    Returns:
        [type] -- [description]
    """

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

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "oIds"]

    """
    MULTI_CALCULATE = True
    Usado para definir se o calculo será executado para cada elemento do get_query()
    """
    MULTI_CALCULATE = False

    JOIN_ON_MULTI = False

    FORCE_RECALCULATE_BASE = False

    EVALUATE_ON_REFERENCE_PAYROLL = False

    FULL_VALUE = False

    CAN_UPDATE_CID = False

    FIELD_RETURN_TO_BASE_VALUE = "correct_value"

    FIELD_RETURN_TO_BASE_SS = "correct_contribution_base"

    USE_OID = False

    """
    Indica se o get_query sera filtrado pela existencia de algum lancamento com mesmo CID
    0: Nao filtra
    1: Filtrar CID repetidos apenas dentro da mesma folha
    2: Filtrar CID repetidos na mesma referencia
    3: Filtrar CID ja existente, independente de quando ocorreu o pagamento
    """
    FILTER_QUERY = 0

    """
     Indica se o calculo vai incidir sobre todas as verbas do periodo,
     inclusive de folhas diferentes ou se apenas da folha em questão
    """
    ALL_PAYROLL = False

    """
    Indica sobre quais lancamentos o base_value_query incidira:
    1: Calcular sobre lancamentos dentro do próprio contracheque, independente da referencia
    2: Calcular sobre lancamentos do mesmo periodo do contracheque
    3: Calcular sobre lancamentos de mesma referencia do calculo
    """
    CALCULATE_OVER = 1

    CID_OBJ_KEY = "pk"

    def __init__(self, employee, payroll, event, entry=None, cid=None, **kwargs):
        """[summary]

        Arguments:
            employee {[type]} -- [description]
            payroll {[type]} -- [description]
            event {[type]} -- [description]

        Keyword Arguments:
            entry {[type]} -- [description] (default: {None})
            cid {[type]} -- [description] (default: {None})
        """
        # log.debug('%s - %s, %s (%s) -> %s --%s--' %(employee, payroll, event, entry, cid, kwargs))
        # log.debug('>>> %s <<< %s - %s' % (self.__class__, cid, kwargs))
        self.cfg = Configuration.get_or_create("gfp")
        self.payroll = payroll
        self.employee = employee
        self.event = event
        self.entry = entry
        self.exclude_events = (
            kwargs["exclude_events"] if "exclude_events" in kwargs else []
        )
        self.only_events = kwargs["only_events"] if "only_events" in kwargs else []
        self.year = kwargs["year"] if "year" in kwargs else self.payroll.periodo.ano
        self.month = kwargs["month"] if "month" in kwargs else self.payroll.periodo.mes
        self.range_salary = NewDateRange.from_month(self.year, min(self.month, 12))
        self.validity = self.range_salary
        self.group_key_cache = kwargs.get("group_cache", None)
        self.pensioner = kwargs.get("pensioner", None)
        self.force_recalculate = (
            kwargs.get("force_recalculate", False)
            or self.FORCE_RECALCULATE_BASE
            or kwargs.get("full_value", False)
        )
        self.full_value = kwargs.get("full_value", False)
        self._cid = cid
        self.force_create = kwargs.get("force_create", None)

        # Carregando apenas os params que poder ser passados para o calculo. Definidos em @PARAMS_
        # log.debug('PARAMS FOR B: %s - %s' % (self.event, kwargs['params'] if 'params' in kwargs else []))
        self.params = {}
        if "params" in kwargs:
            for p in kwargs["params"]:
                if p in self.PARAMS_:
                    self.params[p] = kwargs["params"][p]

        # REMOVING DATA BUG
        if "oIds" in self.params and self.params["oIds"] == [""]:
            self.params.pop("oIds")

        self.configure()
        # log.debug('IC >>>> %s - %s %s > %s' %
        #           (self.event.numero, self.entry.pk if self.entry else 'XXXXXX', self.params, self.focuses_on))

    def configure(self):
        pass

    @property
    @cache_return
    def range_base(self):
        last_day = (
            (self.employee.data_desligamento - relativedelta(days=1))
            if self.employee.data_desligamento
            else None
        )
        return NewDateRange(
            self.range_salary.intersect(
                NewDateRange(self.employee.data_exercicio, last_day)
            )
        )

    @property
    def reference_payroll(self):
        _payroll = self.payroll
        if self.CALCULATE_OVER in [
            3,
        ] and (
            self.references[0] != self.payroll.periodo.ano
            or self.references[1] != self.payroll.periodo.mes
        ):
            # Tentar modificar a folha para a folha do período de referência do calculo ,
            q_payroll = Payroll.objects.filter(
                periodo__ano=self.references[0], periodo__mes=self.references[1]
            )
            _payroll = q_payroll.filter(tipo_folha=self.payroll.tipo_folha).first()
            if not _payroll:
                _payroll = q_payroll.filter(tipo_folha__principal=True).first()

        return _payroll or self.payroll

    @property
    def identification_payroll(self):
        return "%04d%02d" % (
            self.range_salary.first.year,
            self.range_salary.first.month,
        )

    @property
    @cache_return
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

    @cache_return
    def maximum_quantity(self):
        if self.event and self.event.max_quantity_at(self.range_salary.first):
            return float(self.event.max_quantity_at(self.range_salary.first))
        return 0.00

    @cache_return
    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)
            if self.event.quantity_at(self.range_salary.first) is not None:
                return float(self.event.quantity_at(self.range_salary.first))
        return self.maximum_quantity()

    @cache_return
    def factor_quantity(self):
        factor = 1.0
        # if not self.full_value:
        try:
            factor = float(self.quantity()) / float(self.maximum_quantity())
        except ZeroDivisionError:
            factor = 1.0
        except Exception as e:
            log.exception(e)

        return factor

    @cache_return
    def percentage(self):
        pct = 100.0
        if self.event:
            if self.params.get("pct") and self.event.tipo_calculo in [1, 5]:
                pct = float(self.params["pct"])
            if self.event.percentage_at(self.range_salary.first):
                pct = float(self.event.percentage_at(self.range_salary.first))
        # log.debug('PORCENTAGEM de BaseCalculo: %s' % pct)
        return pct

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

    def base_socialsecurity(self, total=False):
        """
        Este calculo deve ser sobrescrito para todo calculo que
        se deseja saber a base previdenciária utilizada pelo calculo
        """
        # log.info('BP de BaseCalculo')
        return self._base_values()[1]

    def full_base_socialsecurity(self):
        pass

    @cache_return
    def base_discounts(self):
        return 0.0

    @property
    def focuses_on(self):
        focuses_on = []
        if self.event:
            focuses_on = [
                e.numero for e in self.event.focuses_on_at(self.range_salary.first)
            ]
        # if self.only_events:
        focuses_on = [
            event_number
            for event_number in focuses_on
            if (event_number in self.only_events or not self.only_events)
            and event_number not in self.exclude_events
        ]
        return focuses_on

    def focuses_on_used(self):
        return None

    def _get_value_from_calc(self, calc, full_value=False):
        return calc.value()

    def _get_value_from_entry(self, entry):
        return float(
            entry.correct_valor
        )  # if self.full_value is False else entry.valor_base)

    def _get_base_ss_from_calc(self, calc):
        return calc.base_socialsecurity()

    def _get_base_ss_from_entry(self, entry):
        return float(
            entry.correct_base_previdencia
            if entry.evento.tipo == "P"
            else -entry.correct_base_previdencia
        )

    def base_value_query(self):
        q_entries = Q(
            evento__numero__in=self.focuses_on,
            contracheque__servidor=self.employee,
            contracheque__pensioner=self.pensioner,
        )
        """
        CALCULATE_OVER
        Indica sobre quais lancamentos o base_value_query incidira:
        1: Calcular sobre lancamentos dentro do próprio contracheque
        2: Calcular sobre lancamentos do mesmo periodo do contracheque
        3: Calcular sobre lancamentos de mesma referencia do calculo
        """

        if self.CALCULATE_OVER == 2 or self.ALL_PAYROLL:
            q_entries = (
                Q(contracheque__folha__periodo=self.reference_payroll.periodo)
                & q_entries
            )
        elif self.CALCULATE_OVER == 3:
            q_entries = (
                Q(reference_year=self.references[0], reference_month=self.references[1])
                & q_entries
            )
        if self.CALCULATE_OVER == 1:
            q_entries = Q(contracheque__folha=self.payroll) & q_entries

        if self.exclude_events:
            q_entries = Q(q_entries & ~Q(evento__numero__in=self.exclude_events))
        if self.only_events:
            q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))

        return Entry.objects.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )

    def _get_bases(self):
        """Gera as bases do calculo

        Returns:
            list -- BASE_VALUE, BASE_SOCIALSECURITY, DAYS, PCT
        """
        return 0.0, 0.0, 0, 0.0

    # @cache_return
    def _base_values(self):
        # log.debug('******************************* BASE VALUE %s' % self.__class__)
        if "base_value" in self.params:
            return float(self.params["base_value"])

        if self.event and self.event.base_value_at(self.range_salary.first):
            return float(self.event.base_value_at(self.range_salary.first))
        # log.debug(self._get_bases())
        totals = (
            self._get_bases()
            if not self.base_value_query().filter(evento__tipo="P").exists()
            else (0.0, 0.0, 0, 0.0)
        )
        total_base, total_base_socialsecurity, total_days, pct = totals
        if not self.payroll:
            for num in self.focuses_on:
                ev = Event.objects.get(numero=num)
                if ev.automated:
                    print(ev, ev.calculation)
                    calc = ev.calculation.cls(
                        self.employee,
                        None,
                        ev,
                        month=self.month,
                        year=self.year,
                        force_create=True,
                    )
                    value = calc.value()
                    base_socialsecurity = calc.base_socialsecurity()
        if not self.force_recalculate:
            totals = self.base_value_query().aggregate(
                tbasev=Sum(self.FIELD_RETURN_TO_BASE_VALUE),
                tbasess=Sum(self.FIELD_RETURN_TO_BASE_SS),
            )

            total_base += float(totals["tbasev"] or 0)
            total_base_socialsecurity += float(totals["tbasess"] or 0)
            # log.debug('AC >>>>   %s(%02d/%04d) %d >>>> %s  %s' % (
            #     self.event.numero if self.event else 'XXXXX',
            #     self.references[1],
            #     self.references[0],
            #     self.base_value_query().count(),
            #     total_base,
            #     total_base_socialsecurity
            # ))
        else:
            for fe in self.base_value_query():
                cc = False
                # (fe.reference_year != self.year or fe.reference_month != self.month or self.force_recalculate):
                if fe.evento.automated and fe.classcode and self.force_recalculate:
                    params = {
                        "pct": fe.correct_pct,
                        "qnt": fe.correct_qnt,
                        "info": fe.info,
                        "patronal": fe.correct_employer_contribution,
                        "valor_base": fe.correct_base_value,
                    }
                    params.update(fe.vars)
                    calc = fe.classcode.cls(
                        self.employee,
                        self.reference_payroll,
                        fe.evento,
                        entry=fe,
                        cid=fe.cid,
                        year=self.references[0],
                        month=min(self.references[1], 12),
                        params=params,
                        only_events=self.focuses_on or self.only_events,
                        exclude_events=self.exclude_events,
                        group_cache=self.group_key_cache,
                        pensioner=fe.contracheque.pensioner,
                        force_recalculate=self.force_recalculate,
                        full_value=self.full_value or self.FULL_VALUE,
                    )
                    # log.debug(self)
                    value = self._get_value_from_calc(calc)
                    base_socialsecurity = self._get_base_ss_from_calc(calc)
                    cc = True
                else:
                    cc = False
                    value = self._get_value_from_entry(fe)
                    base_socialsecurity = self._get_base_ss_from_entry(fe)
                value = value if fe.evento.tipo == "P" else -abs(value)
                # log.debug('%s >>>> %s >>>> %s : %s + %s = %s' % ('CC' if cc else 'NC',
                #                                                  self.event.numero if self.event else 'XXX-XX',
                #                                                  fe.evento.numero,
                #                                                  total_base,
                #                                                  value,
                #                                                  total_base + value))
                total_base += value
                total_base_socialsecurity += (
                    base_socialsecurity
                    if fe.evento.tipo == "P"
                    else -base_socialsecurity
                )

        total_base -= self.base_discounts()

        if self.event and self.event.calculo_invertido:
            total_base, total_base_socialsecurity = (
                -total_base,
                -total_base_socialsecurity,
            )

        return total_base, total_base_socialsecurity, total_days, pct

    @cache_return
    def base_value(self):
        return self._base_values()[0]

    @property
    @cache_return
    def ceiling(self):
        return (
            float(self.event.ceiling_at(self.range_salary.first))
            if self.event and self.event.ceiling_at(self.range_salary.first)
            else 9999999.99
        )

    @property
    @cache_return
    def floor(self):
        return (
            float(self.event.floor_at(self.range_salary.first))
            if self.event and self.event.floor_at(self.range_salary.first)
            else 0.00
        )

    @cache_return
    def value(self):
        value = (
            self.base_value()
            * (float(self.percentage()) / 100.00)
            * self.factor_quantity()
        )
        if value:
            value = min(value, self.ceiling)
            value = max(value, self.floor)
        return value

    def full_value(self):
        try:
            return self.value() / self.factor_quantity()
        except ZeroDivisionError:
            return 0.0

    @cache_return
    def employer_value(self):
        if "patronal" in self.params:
            return float(self.params["patronal"])
        return 0.0

    @cache_return
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
        log.debug("CALLBACK for %s" % self.__class__.__name__)

    @property
    def cid(self):
        if (
            not self.entry or self.CAN_UPDATE_CID
        ):  # or self.entry and not self.entry.cid:
            return self.get_cid_for_obj(self.object)
        return self.entry.cid

    def vars(self):
        """
        Por padrão usa-se {oIds: [value1, value2, ...]}
        """
        return {}

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
        cids = [fe.cid for fe in q_entries]
        # log.debug('CIDS: %s' % cids)
        return cids

    def get_query(self):
        return [
            obj
            for obj in self._get_query()
            if getattr(obj, "pk", obj) not in self._exclude_repeated_cids()
        ]

    def choices(self):
        return [
            (self.get_cid_for_obj(obj), self.unicode_for_obj(obj))
            for obj in self.get_query()
        ]

    def extract_salaries_by_cid(self):
        # log.debug(self.employee.remunerationbase_set.filter(salary=self._cid).last())
        return self.employee.remunerationbase_set.filter(salary=self._cid).last()

    @property
    @cache_return
    def object(self):
        if len(self.get_query()) == 1 or len(set(self.get_query())) == 1:
            return self.get_query()[0]
        return None if not self.entry else self.extract_salaries_by_cid()

    def get_params_for_obj(self, obj):
        return {"oIds": [obj.pk if hasattr(obj, "pk") else obj]}

    def get_cid_for_obj(self, obj):
        cid = getattr(
            obj,
            self.CID_OBJ_KEY,
            obj.get(self.CID_OBJ_KEY, obj) if isinstance(obj, dict) else obj,
        )
        if not (isinstance(cid, int) or (isinstance(cid, str) and cid.isdigit())):
            cid = None
        return cid

    def unicode_for_obj(self, obj):
        return "%s - %s" % (obj.identifier, obj.salary)

    @property
    def references(self):
        return (self.year, self.month)

    @property
    def interface(self):
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
            "cid": 0,
        }
        return obj

    def calculate_single(self):
        # log.debug('CALCULAR of %s [%s]' % (self.__class__.__name__, self.params))
        """
        Metodo responsável por realizar o calculo.
        """

        obj = self.interface
        # log.debug(obj)

        try:
            self.validate()
            self.configure()
            log.debug(self.object)
            log.debug("CALCULATE SINGLE %s (%s)" % (self._cid, self.cid))
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
                    "choices": self.choices(),
                    "parcela": self.installment(),
                    "installments_paid": self.installments_paid(),
                    "prazo": self.total_installment(),
                    "cid": self.cid,
                }
            )
            if self.USE_OID:
                obj.update({"oIds": self.params.get("oIds", "")})
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
                log.debug(obj)
                params = self.params.copy()
                # params.update(self.get_params_for_obj(obj))
                # log.debug('CALCULATE MULTI PARAMS %s' % params)
                cid = self.get_cid_for_obj(obj)
                calcs.append(
                    self.__class__(
                        self.employee,
                        self.payroll,
                        self.event,
                        None,
                        cid=cid,
                        params=params,
                        group_cache=self.group_key_cache,
                    ).calculate_single()
                )

        return calcs

    def calculate(self):

        result = self.interface
        try:
            self.validate()
            # self.configure()
        except Exception as e:
            result["validate"]["message"] = str(e)
            return result

        if (
            not self.MULTI_CALCULATE
            or len(self.get_query()) == 1
            or len(set(self.get_query())) == 1
        ):
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
                    # result['oIds'] += calc['oIds']
                    result["valor_base"] += calc["valor_base"]

                result["valor_base"] = (
                    (result["valor_base"] / float(len(self.calculate_multi())))
                    if len(self.calculate_multi()) > 0
                    else 0.00
                )

                return result


class WorkDaysCalculation(BaseCalculation):
    """
    Calculo que utiliza a quantidade de dias de efetivo exercicio no mês de
    referencia da folha para calcular o 'qnt'
    """

    BASE_BUSINESSDAYS = False
    IGNORE_DEPARTURE = False

    def business_days(self, date_range):
        return date_range.business_days if self.BASE_BUSINESSDAYS else date_range.days

    @property
    @cache_return
    def base_days(self):
        return self.business_days(self.range_salary)

    @cache_return
    def get_possessions(self):
        possessions = (
            self.employee.posses.exclude(Q(data_exercicio__gt=self.range_salary.last))
            .filter(
                Q(desligamento=None)
                | Q(desligamento__data_desligamento__gte=self.range_salary.first)
            )
            .distinct()
            .order_by("-data_exercicio")
        )

        return possessions.with_office_valid_in(self.range_salary)

    def _exclude_ranges_for_range_salary(self):
        range_unpaid_absences = NewDateRange()

        if self.IGNORE_DEPARTURE is False:
            for mc in AfastamentoOutroOrgao.objects.filter(
                servidor=self.employee
            ).exclude(
                Q(data_inicio__gt=self.range_salary.last)
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
                    Q(data_fim__lt=self.range_salary.first)
                    | Q(data_inicio__gt=self.range_salary.last)
                )
                .exclude(~Q(afastamento__afastamentooutroorgao=None))
                .exclude(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(
                    absence.data_inicio, absence.data_fim
                )
        # log.debug('SFE ERANGES: %s' % range_unpaid_absences)

        return range_unpaid_absences

    def _intersect_ranges_for_range_salary(self):
        return self.range_salary.intersect(self.validity)

    def range_salary_for(self, possession=None, range_salary=None):
        # log.debug('SFE %s RSF 1: %s' % (self.__class__.__name__, possession))
        if not range_salary:
            range_salary = self._intersect_ranges_for_range_salary()
        ranges_ = NewDateRange()
        # log.debug('SFE %s RSF 2 %s' % (self.__class__.__name__, range_salary))

        if range_salary.days == 0:
            return ranges_

        if not possession:
            for possession in self.get_possessions():
                ranges_ += NewDateRange(
                    possession.data_exercicio,
                    (
                        (possession.financial_effect_date_end - relativedelta(days=1))
                        if possession.financial_effect_date_end
                        else None
                    ),
                )
            possession_request = (
                self.get_possessions()
                .filter(quadro__cargo__tipo_lei_cargo="AC")
                .first()
            )
        else:
            ranges_ = NewDateRange(
                possession.data_exercicio,
                (
                    (possession.financial_effect_date_end - relativedelta(days=1))
                    if possession.financial_effect_date_end
                    else None
                ),
            )
            possession_request = (
                possession if possession.quadro.cargo.tipo_lei_cargo == "AC" else None
            )

        if possession_request:
            ranges_requested_ = NewDateRange()
            for req in possession_request.requisicao.currents_in(range=range_salary):
                ranges_requested_ += NewDateRange(req.data_inicio, req.data_fim)
            ranges_ = ranges_.intersect(ranges_requested_)
        ranges_ = (
            ranges_.intersect(range_salary) - self._exclude_ranges_for_range_salary()
        )
        # log.debug('SFE %s RSF 4 %s' % (self.__class__.__name__, range_salary))

        return ranges_

        # return (ranges_ - range_unpaid_absences) if range_unpaid_absences.days > 0 else ranges_

    def get_possessions_by_type(self, types=[]):
        """
        Retorna as posses de efetivo que o servidor tinha no mes da referencia da folha,
        pois pode ser que o servidor começou o mês com um cargo e depois tomou posse em
        outro sendo exonerado do primeiro
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
        return self.business_days(self.range_salary_for())

    def maximum_quantity(self):
        return self.base_days


class PercentageCalculation(BaseCalculation):
    def percentage(self):
        return 0.00
