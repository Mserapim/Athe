# -*- coding: utf-8 -*-

from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Count, FloatField, Max, Q, Sum

from contrib.cache import get_cache, set_cache
from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.classcodes.base import BaseCalculation, WorkDaysCalculation
from rh.gfp.models import EstruturaTabelaSalarial, FolhaEvento as Entry, Periodo
from rh.models import MovimentacaoSubstituicao as SubstitutionMovement
from standard.models import Configuration, RunCodeManager

# from django.db.models.aggregates import Avg


log = getLogger(__name__)


@RunCodeManager.register("gfp-classcodes-basesalary")
class BaseSalary(WorkDaysCalculation):
    title = "Calculo Base para remuneração"
    description = """
        Este cálculo pode ser usado como base para remuneração em geral.
        Se for usado diretamente será retornado o valor da remuneração total
        do servidor (efetivo + (função ou (gratification + comissão) + eletivo + extras)
    """

    INCLUDE_EXTRASPAYMENTS = [
        "VPI",
    ]
    FULL_VALUE = False

    TYPES = ["EF", "AC", "CM", "FC", "EL", "EX"]

    CID_OBJ_KEY = "salary"

    """
    Exclude from extract_base_salary_by_type the possessions with match the pairs of type employee(M/S/E) -
    p.servidor.tipo and type of job position('EF', 'AC', 'CM', 'FC', 'EL') - p.quadro.cargo.tipo.
    Ex.: EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {'M': ['CM', 'EL']} # this config exclude all salaries
    comissioned or efective of members
    """
    EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {}

    def resolve_period(self):
        try:
            p = Periodo.objects.get(mes=self.month, ano=self.year)
        except Periodo.DoesNotExist:
            o = Periodo.objects.first()
            p = o
            p.mes = self.month
            p.ano = self.year
            p.pk = None
            p.save()
        return p

    def extract_salaries_by_period(self, period=None):
        if not period:
            if not self.payroll:
                period = self.resolve_period()
            else:
                period = self.payroll.periodo
        period_bases = self.extract_salaries_by_type(period).periods()
        base_list = []
        for p in period_bases:
            validity = p.range_period().intersect(self.validity)
            if validity.days > 0:
                base_list.append(p.pk)
        return (
            self.employee.remunerationbase_set.periods()
            .filter(pk__in=base_list)
            .of_period(period)
        )

    def extract_salaries_by_type(self, period=None, types=[]):
        if not period and self.payroll:
            period = self.payroll.periodo
        else:
            period = self.resolve_period()
        if not types:
            types = self.TYPES
        of_period = self.employee.remunerationbase_set.of_period(period)
        if self.force_create:
            of_period = self.employee.remunerationbase_set.of_period_create(
                period, self.force_create
            )
        return of_period.filter(link__in=types)

    def base_salary_for_type(self, types=[], only_with_onus=True, cid=None):
        if not types:
            types = self.TYPES
        cache_id = "CBS%s%s%s%s" % (
            self.identification_payroll,
            self.employee.matricula,
            "".join(types),
            cid,
        )
        # log.debug('CALCULATE BSFT %s - %s' % (types, cid))

        # if get_cache(cache_id, self.group_key_cache):
        # return get_cache(cache_id, self.group_key_cache)

        periods = self.extract_salaries_by_period().filter(remuneration__link__in=types)
        if cid or self.entry:
            periods = periods.filter(remuneration__salary=cid)
        if only_with_onus:
            periods = periods.filter(remuneration__onus=True)

        totals = periods.aggregate(
            bv=Avg("base_value"),
            nbv=Sum("normal_value", output_field=FloatField()),
            v=Sum("value", output_field=FloatField()),
            bg=Sum("base_gratification", output_field=FloatField()),
            nbg=Sum("normal_gratification", output_field=FloatField()),
            g=Sum("gratification", output_field=FloatField()),
            d=Sum("days", output_field=FloatField()),
            pctg=Max("remuneration__base_gratification", output_field=FloatField()),
            pctv=Max("remuneration__base_value", output_field=FloatField()),
            periods=Count("pk"),
        )
        pct = periods.filter(remuneration__percentage=True).exists()

        only_one_period = totals["periods"] == 1
        salary = {
            "value": totals["v"] or 0,
            "gratification": totals["g"] or 0,
            "days": totals["d"] or 0,
            "normal_base_value": totals["bv" if only_one_period else "nbv"] or 0,
            "normal_base_gratification": totals["bg" if only_one_period else "nbg"]
            or 0,
            "base_value": totals["bv"] or 0,
            "base_gratification": totals["bg"] or 0,
            "pct_grat": totals["pctg"] if pct else 100.0,
            "pct_value": totals["pctv"] if pct else 100.0,
            "onus": periods.filter(remuneration__onus=True).exists(),
        }
        set_cache(cache_id, salary, self.group_key_cache)

        return salary

    def _get_query(self):
        if self._cid:
            return [
                _id
                for _id in self.extract_salaries_by_type()
                if str(_id.salary) == str(self._cid)
            ]
        if not self.entry:
            return self.extract_salaries_by_type()
        return []

    def new_base_salary(self):
        total = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "normal_base_value": 0.0,
            "normal_base_gratification": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "normal_base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
            "normal_base_extra": 0.0,
        }
        salaries = self.extract_salaries_by_period()
        ef_ = salaries.filter(remuneration__link__in=["EF", "AC"])
        cm_ = salaries.filter(remuneration__link__in=["CM", "FC", "EL"])
        ex_ = salaries.filter(remuneration__link="EX")
        if self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(self.employee.tipo, []):
            if "CM" not in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(
                self.employee.tipo, False
            ):
                cm_ = salaries.filter(remuneration__link__in=["CM"])
            elif "FC" not in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(
                self.employee.tipo, False
            ):
                cm_ = salaries.filter(remuneration__link__in=["FC"])
            elif "EL" not in self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB.get(
                self.employee.tipo, False
            ):
                cm_ = salaries.filter(remuneration__link__in=["EL"])
        log.debug("BASE SALARY >> EF: %s CM: %s" % (ef_, cm_))
        value_ef = (
            ef_.aggregate(Sum("value", output_field=FloatField()))["value__sum"] or 0.0
        )
        value_ex = (
            ex_.aggregate(Sum("value", output_field=FloatField()))["value__sum"] or 0.0
        )
        value_cm = (
            cm_.aggregate(Sum("value", output_field=FloatField()))["value__sum"] or 0.0
        )
        normal_value_ex = (
            ex_.aggregate(Sum("normal_value", output_field=FloatField()))[
                "normal_value__sum"
            ]
            or 0.0
        )
        normal_value_cm = (
            cm_.aggregate(Sum("normal_value", output_field=FloatField()))[
                "normal_value__sum"
            ]
            or 0.0
        )
        total["gratification"] = (
            cm_.aggregate(Sum("gratification", output_field=FloatField()))[
                "gratification__sum"
            ]
            or 0.0
        )
        total["normal_base_extra"] = value_ex
        total["normal_base_gratification"] = (
            cm_.aggregate(Sum("normal_gratification", output_field=FloatField()))[
                "normal_gratification__sum"
            ]
            or 0.0
        )
        total["days"] = (
            cm_.aggregate(Sum("days"))["days__sum"] or 0
            if self.employee.tipo_servidor == "CM"
            else ef_.aggregate(Sum("days"))["days__sum"] or 0
        )
        normal_value_ef = (
            ef_.aggregate(Sum("normal_value", output_field=FloatField()))[
                "normal_value__sum"
            ]
            or 0.0
        )
        value = (
            value_ef + normal_value_ex
            if value_ef + normal_value_ex > value_cm
            else value_cm
        )
        normal_value = (
            normal_value_ef + normal_value_ex
            if normal_value_ef + normal_value_ex > normal_value_cm
            else normal_value_cm
        )
        total["value"] = value
        total["normal_base_value"] = normal_value

        total["base_socialsecurity"] = value
        total["normal_base_socialsecurity"] = normal_value

        ssc = self.employee.get_socialsecurity_by_validity(
            range=self.payroll.date_range
        )
        regime_social_security = ssc.regime if ssc else None
        if regime_social_security == 1:
            total["base_socialsecurity"] = total["gratification"] + value
            total["normal_base_socialsecurity"] = (
                total["normal_base_gratification"] + normal_value
            )
        else:
            total["base_socialsecurity"] = value_ef + value_ex
            total["normal_base_socialsecurity"] = normal_value_ef + normal_value_ex

        # Removendo remuneração extra caso o valor da soma do extra e da base for menor que o valor do comissionado
        total["normal_base_extra"] = (
            total["normal_base_extra"]
            if value_ef + normal_value_ex > value_cm
            else 0.00
        )
        total["extra"] = value_ex
        total["base_value"] = total["normal_base_value"]
        total["base_gratification"] = total["normal_base_gratification"]
        total["full_base_socialsecurity"] = total["normal_base_socialsecurity"]
        total["base_extra"] = total["normal_base_extra"]
        total["base_days"] = self.base_days
        return total

    def _get_bases(self):
        base = self.new_base_salary()
        if self.full_value:
            total_base = (
                base["base_value"] + base["base_gratification"]
            )  # + base['base_extra']
        else:
            total_base = base["value"] + base["gratification"]
        total_base_socialsecurity = base["full_base_socialsecurity"]
        return total_base, total_base_socialsecurity, base["base_days"], 0.0

    @cache_return
    def base_value(self):
        return self._base_values()[0]

    def quantity(self):
        return self._base_values()[2]

    def base_socialsecurity(self):
        return self._base_values()[1]

    def _event_information(self, types=[]):
        info = []
        salaries = self.extract_salaries_by_type()
        for salary in salaries:
            info.append("%s" % salary.identifier)
        return "-".join(info)

    def cache_value(self, value_type):
        salaries = self.extract_salaries_by_period().filter(
            remuneration__link__in=self.TYPES
        )
        real_value = "" if not self.full_value else "normal_"
        return (
            salaries.aggregate(Sum(real_value + value_type, output_field=FloatField()))[
                real_value + value_type + "__sum"
            ]
            or 0.0
        )

    @property
    def identifier(self):
        return ""


@RunCodeManager.register("gfp-classcodes-salaryeffective")
class SalaryEffective(BaseSalary):
    title = "Remuneração de efetivo apenas"
    description = """
        Este cálculo retorna o valor do salário de efetivo, caso o servidor seja efetivo, ou seja,
        apenas o valor da tabela salarial do cargo efetivo do servidor.
    """

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False

    TYPES = [
        "EF",
    ]

    @property
    def identifier(self):
        return self.object.identifier

    def validate(self):
        self.validate_not_paycheck_pension()
        if "EF" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não é efetivo no período" % (self.employee)
            )

    def _get_bases(self):
        base = self.base_salary_for_type(cid=self.cid)

        return (
            float(base["base_value"]),
            float(base["normal_base_value"]),
            float(base["days"]),
            0.0,
        )

    def quantity(self):
        # log.debug('RECALCULATE QNT: %s %s' % (self.object, self._get_bases()[2]))
        return int(self._get_bases()[2])

    def base_socialsecurity(self):
        # log.debug(self.__class__)
        return self.value()

    def event_information(self):
        info = []
        salaries = self.extract_salaries_by_type()
        for salary in salaries:
            if self.cid and salary.salary == int(self.cid):
                info.append("%s" % salary.identifier)
        return "-".join(info)


@RunCodeManager.register("gfp-classcodes-salaryrequested")
class SalaryRequested(SalaryEffective):
    title = "Remuneração de servidor requisitado"
    description = """
    """
    TYPES = [
        "AC",
    ]
    INCLUDE_EXTRASPAYMENTS = ["VPI", "INCENTIVO-A-DOCENCIA"]

    def validate(self):
        self.validate_not_paycheck_pension()
        if "AC" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não é requisitado no período" % (self.employee)
            )

    def _get_bases(self):
        base = self.base_salary_for_type(cid=self.cid)
        return (
            float(base["normal_base_value"]),
            float(base["normal_base_value"]),
            float(base["days"]),
            0.0,
        )

    def event_information(self):
        if "info" in self.params:
            return self.params["info"]
        return ""


@RunCodeManager.register("gfp-classcodes-gratificationfunction")
class GratificationFunction(SalaryEffective):
    title = "Gratificação de função de confiança"
    description = """
    Usado exclusivamente para quem possui função de confiança.
    O calculo retornará o valor da gratificação da função proporcional aos
    dias trabalhos com a função!
    """

    TYPES = [
        "FC",
    ]

    def validate(self):
        self.validate_not_paycheck_pension()
        if "FC" not in self.employee_types:
            raise self.CalculationNotApplicable(
                "O Servidor %s não possui função de confiança no período"
                % (self.employee)
            )

    @property
    @cache_return
    def _base_value(self):
        if not self.object:
            return 0.00, 0, 0.0

        base_value = pct = 0.00
        days = 0
        salaries = self.extract_salaries_by_period()
        for salary in salaries:
            obj = "%s%s" % (salary.remuneration.link, salary.remuneration.identifier)
            if obj == self.object:
                base_value = (
                    salary.normal_value
                    if (
                        salary.remuneration.percentage
                        and salary.remuneration.base_gratification > 0
                    )
                    else salary.remuneration.base_gratification
                )
                pct = (
                    salary.remuneration.base_gratification
                    if salary.remuneration.percentage
                    else 100
                )
                days += salary.range_period().days

        return base_value, days, pct

    def base_value(self):
        return self.base_salary_for_type([self.object.link], True, self.cid)[
            "base_gratification"
        ]

    def percentage(self):
        return (
            float(
                self.base_salary_for_type([self.object.link], True, self.cid)[
                    "pct_grat"
                ]
            )
            or 100.0
        )

    def value(self):
        try:
            value = self.base_salary_for_type([self.object.link], True, self.cid)[
                "gratification"
            ]
        except AttributeError:
            value = 0.0
        return value


@RunCodeManager.register("gfp-classcodes-salarycommissioned")
class SalaryCommissioned(SalaryEffective):
    title = "Vencimento de comissionado"
    description = """
    Usado exclusivamente para quem possui cargo em comissão ou eletivo (Ex.: DAM, PGJ, AEPGJ, CGJ, etc).
    O calculo retornará o valor da parte vencimental do cargo, proporcional aos
    dias trabalhos no mesmo!
    """
    TYPES = ["CM", "EL"]

    def extract_salaries_by_type(self, period=None, types=[]):
        if not types:
            types = self.TYPES
        return super(SalaryCommissioned, self).extract_salaries_by_type(
            types=types
        )  # .filter(link__in=types)

    def validate(self):
        self.validate_not_paycheck_pension()
        if not set(self.employee_types).intersection(["CM", "EL"]):
            raise self.CalculationNotApplicable(
                "O Servidor %s não possui cargo comissionado no período"
                % (self.employee)
            )
        if set(self.employee_types).intersection(["AC", "EF"]):
            raise self.CalculationNotApplicable(
                "Essa verba é para servidor exclusivamente comissionado!"
            )

    @cache_return
    def _exclude_ranges_for_range_salary(self):
        range_ = NewDateRange()
        if not set(self.employee_types).intersection(["AC", "EF"]):
            # Excluindo os periodos de salario maternidade (INSS - 120 dias)
            query_advances = self.employee.departures(
                self.payroll.periodo.range.first, self.payroll.periodo.range.last
            )
            for lm in query_advances.filter(tipo=12):  # MATERNIDADE
                range_ += NewDateRange(
                    lm.data_inicio,
                    min(lm.data_fim, lm.data_inicio + relativedelta(days=119)),
                )

        return (
            range_ + super(SalaryCommissioned, self)._exclude_ranges_for_range_salary()
        )


@RunCodeManager.register("gfp-classcodes-maternitypay")
class MaternitySalary(SalaryCommissioned):
    title = "Salário Maternidade"
    description = """
    Usado exclusivamente para quem possui exclusivamente cargo em comissão(Ex.: DAM, AEPGJ, etc) e .
    está em licença maternidade. O calculo retornará o valor da parte vencimental + gratificação do cargo,
    proporcional aos dias de licença no periodo!
    """
    TYPES = [
        "SM",
    ]

    @cache_return
    def _exclude_ranges_for_range_salary(self):
        return NewDateRange()

    def _intersect_ranges_for_range_salary(self):
        intersect_range = super(
            MaternitySalary, self
        )._intersect_ranges_for_range_salary()
        range_ = NewDateRange()
        # Excluindo os periodos de salario maternidade (INSS - 120 dias)
        query_advances_maternity = self.employee.departures(
            self.payroll.periodo.range.first, self.payroll.periodo.range.last
        ).filter(tipo=12)
        for lm in query_advances_maternity:
            range_ += NewDateRange(
                lm.data_inicio,
                min(lm.data_fim, lm.data_inicio + relativedelta(days=119)),
            )

        # log.debug(u'SFE %s' % range_)
        return intersect_range.intersect(range_)

    @cache_return
    def _base_values(self):
        if not self.object:
            return 0.00, 0

        # _type = self.object[0:2]
        base_value = 0.00
        days = 0
        for salarie in self.extract_salaries_by_type().filter(
            identifier=self.object.identifier
        ):
            base_value = float(salarie.base_value + salarie.base_gratification)
            days += salarie.days_by_period(self.payroll.periodo)

        return base_value, days

    def employer_value(self):
        return -self.value()


@RunCodeManager.register("gfp-classcodes-gratificationcomissioned")
class GratificationCommissioned(GratificationFunction):
    """Usado exclusivamente para quem possui cargo em comissão.

    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """

    title = "Gratificação do cargo em comissão"
    description = """
    Usado exclusivamente para quem possui cargo em comissão.
    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """
    TYPES = ["CM", "EL"]

    def configure(self):
        if self.employee.tipo == "M" and self.object:
            if self.object.identifier in ["CSUP", "CGPGJ", "CGAECO", "DAM7", "AEPGJ"]:
                # 06/01/2016 data de início da indenização
                self.validity = NewDateRange(None, datetime(2016, 1, 6))
            elif self.object.identifier in ["PGJ", "SUBPGJ", "OGJ", "CGJ"]:
                # 27/03/2016 data de início da indenização para esses cargos
                self.validity = NewDateRange(None, datetime(2016, 3, 27))

            self.validity += NewDateRange(datetime(2017, 9, 1), None)
        # log.debug('CONFIGURE OBJ: %s/%s %s' % (self.object, self.object[2:], unicode(self.validity)))

    def validate(self):
        self.validate_not_paycheck_pension()
        if not set(self.employee_types).intersection(["CM", "EL"]):
            raise self.CalculationNotApplicable(
                "O Servidor %s não possui cargo comissionado no período"
                % (self.employee)
            )

    @cache_return
    def _exclude_ranges_for_range_salary(self):
        range_ = NewDateRange()
        if not set(self.employee_types).intersection(["AC", "EF"]):
            # Excluindo os periodos de salario maternidade (INSS - 120 dias)
            query_advances_maternity = self.employee.departures(
                self.payroll.periodo.range.first, self.payroll.periodo.range.last
            ).filter(tipo=12)
            for lm in query_advances_maternity:
                range_ += NewDateRange(
                    lm.data_inicio,
                    min(lm.data_fim, lm.data_inicio + relativedelta(days=119)),
                )
        return (
            range_
            + super(GratificationCommissioned, self)._exclude_ranges_for_range_salary()
        )

    def base_socialsecurity(self):
        ssc = self.employee.get_socialsecurity_by_validity(
            range=self.payroll.date_range
        )
        regime_social_security = ssc.regime if ssc else None
        return 0 if regime_social_security in [2, 3] else self.value()


@RunCodeManager.register("gfp-classcodes-indemnificationcomissioned")
class IndemnificationCommissioned(GratificationCommissioned):
    """Usado exclusivamente para quem possui cargo em comissão.

    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """

    title = "Gratificação do cargo em comissão"
    description = """
    Usado exclusivamente para quem possui cargo em comissão.
    O calculo retornará o valor da gratificação do cargo proporcional aos
    dias trabalhos no mesmo!
    """
    TYPES = ["CM", "EL"]

    def configure(self):
        if self.employee.tipo == "M" and self.object:
            if self.object[2:] in ["CSUP", "CGPGJ", "CGAECO", "DAM7", "AEPGJ"]:
                self.validity = NewDateRange(
                    datetime(2016, 1, 7), datetime(2017, 8, 31)
                )
            elif self.object[2:] in ["PGJ", "SUBPGJ", "OGJ", "CGJ"]:
                # 28/03/2016 data de início da indenização para esses cargos
                self.validity = NewDateRange(
                    datetime(2016, 3, 28), datetime(2017, 8, 31)
                )
        else:
            self.validity = NewDateRange()
        # log.debug('CONFIGURE OBJ: %s/%s %s' % (self.object, self.object[2:], unicode(self.validity)))

    def validate(self):
        self.validate_not_paycheck_pension()
        if not self.employee.tipo == "M" or not set(self.employee_types).intersection(
            ["CM", "EL"]
        ):
            raise self.CalculationNotApplicable(
                "Cálculo exclusivo para membros com cargos comissionados/eletivos!"
                % (self.employee)
            )


@RunCodeManager.register("gfp-classcodes-complementsalarycommissioned")
class ComplementSalaryCommissioned(SalaryCommissioned):
    title = "Complemento do vencimento de comissionado"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da diferença entre a parte vencimental do cargo comissionado e a do cargo efetivo,
    proporcional aos dias trabalhos no mesmo!
    """
    USE_OID = True

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
        log.debug(
            "%s - %s, %s (%s) -> %s --%s--"
            % (employee, payroll, event, entry, cid, kwargs)
        )
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
        self.params = {}
        if "params" in kwargs:
            for p in kwargs["params"]:
                if p in self.PARAMS_:
                    self.params[p] = kwargs["params"][p]
        if not self._cid and "oIds" in self.params:
            self._cid = self.params["oIds"][0]
        log.debug(self._cid)
        log.debug(self.params)

        self.configure()

    @property
    @cache_return
    def object(self):
        log.debug(self.get_query())
        if len(self.get_query()) == 1 or len(set(self.get_query())) == 1:
            return self.get_query()[0]
        return self.extract_salaries_by_cid()

    def extract_salaries_by_type(self, period=None):
        return (
            super(ComplementSalaryCommissioned, self)
            .extract_salaries_by_type(types=BaseSalary.TYPES)
            .only_with_onus()
        )

    def validate(self):
        self.validate_not_paycheck_pension()
        if not (
            "CM" in self.employee_types
            and ("EF" in self.employee_types or "AC" in self.employee_types)
        ):
            raise self.CalculationNotApplicable(
                "O Servidor precisa ser efetivo e comissionado no período!"
            )

    @property
    @cache_return
    def _base_value(self):
        base_value = days = 0.0
        salaries = self.extract_salaries_by_period()
        salaries_period_cm = salaries.filter(
            remuneration__link__in=("CM",), remuneration__identifier=self.identifier
        )
        for scm in salaries_period_cm:
            ef_ = salaries.filter(
                remuneration__link__in=("EF", "AC"), start=scm.start, end=scm.end
            )
            # cm_ = salaries.filter(remuneration__link__in=('CM',))
            ex_ = salaries.filter(
                remuneration__link__in=("EX",), start=scm.start, end=scm.end
            )
            if ef_.exists():
                value_ef = float(ef_.aggregate(Sum("value"))["value__sum"] or 0)
                value_cm = float(scm.value)
                value_ex = float(ex_.aggregate(Sum("value"))["value__sum"] or 0)
                base_value += value_cm - value_ef - value_ex
                days += scm.days

        return (base_value / days * self.base_days) if base_value > 0 else 0, days

    def base_value(self):
        return float(self._base_value[0])

    def quantity(self):
        return self._base_value[1]

    @property
    @cache_return
    def _tcid(self):
        return (
            self._cid[2:] if len(self._cid) > 5 and self._cid[:2] == "CM" else self._cid
        )

    def get_query(self):
        if self._cid:
            return (
                super(ComplementSalaryCommissioned, self)
                .extract_salaries_by_type()
                .filter(identifier=self._tcid)
            )
        return super().extract_salaries_by_type().filter(link__in=self.TYPES)

    def choices(self):
        return [(obj.identifier, self.unicode_for_obj(obj)) for obj in self.get_query()]

    def event_information(self):
        return "%s" % self.object.identifier


@RunCodeManager.register("gfp-classcodes-complementgratificationcommissioned")
class ComplementGratificationCommissioned(GratificationCommissioned):
    title = "Complemento da grtificação de comissionado"
    description = """
    Usado exclusivamente para quem possui cargo em comissão e é efetivo.
    O calculo retornará o valor da gratificação do cargo comissionado, proporcional
    aos dias trabalhos no mesmo!
    """

    def validate(self):
        self.validate_not_paycheck_pension()
        if not (
            ("CM" in self.employee_types or "EL" in self.employee_types)
            and ("EF" in self.employee_types or "AC" in self.employee_types)
        ):
            raise self.CalculationNotApplicable(
                "O Servidor precisa ser efetivo e comissionado no período!"
            )


@RunCodeManager.register("gfp-classcodes-extra-vpi")
class IdentifiedPersonalAdvantage(SalaryEffective):
    title = "Cálculo de Vantagem Pessoal Identificada"
    description = """
    Usado exclusivamente para quem possui VPI (servidores efetivos antigos).
    O calculo retornará o valor da VPI do servidor, cadastrada no Gestor de Verbas Adicionais,
    proporcional aos dias trabalhados
    """

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False

    TYPES = [
        "EX",
    ]

    @property
    def identifier(self):
        return "VPI"

    def base_socialsecurity(self):
        return self.value()

    def event_information(self):
        base = self.extract_salaries_by_type(types=["EF"])
        if base.exists():
            return base.get().identifier


@RunCodeManager.register("gfp-classcodes-reduce-salary-cap")
class ReduceSalaryCap(BaseCalculation):
    title = "Redutor de Teto Constitucional"
    description = """
    Usado para todos os servidores. No entanto, o teto é configurado separadamente para
    servidores e membros no menu FOLHA DE PAGAMENTO > Parâmentros > Período.
    O calculo retornará a diferença entre a remuneração recebida e o teto
    """

    FORCE_RECALCULATE_BASE = True

    @property
    @cache_return
    def object(self):
        log.debug(self.get_query())
        if len(self.get_query()) == 1 or len(set(self.get_query())) == 1:
            return self.get_query()[0]
        return None

    @property
    def salary_cap(self):
        if self.employee.tipo == "M":
            return float(self.reference_payroll.periodo.salario_teto_membros or 0.00)
        else:
            return float(self.reference_payroll.periodo.salario_teto_adm or 0.00)

    @cache_return
    def value(self):
        cap_value = self.salary_cap
        base_value = float(self.base_value())
        if cap_value and base_value > cap_value:
            return base_value - cap_value
        else:
            return 0.0

    @cache_return
    def base_socialsecurity(self):
        sum_base = sum_base_ss = 0.00
        value = self.value()

        for fe in self.reference_payroll.lancamentos.exclude(
            evento__numero__in=self.exclude_events
        ).filter(evento__numero__in=self.focuses_on, servidor=self.employee):
            sum_base += float(
                fe.correct_valor if fe.evento.tipo == "P" else -fe.correct_valor
            )
            sum_base_ss += float(
                fe.correct_contribution_base
                if fe.evento.tipo == "P"
                else -fe.correct_contribution_base
            )

        diff_ss = sum_base - sum_base_ss

        if diff_ss > value:
            return 0.00
        else:
            return value - diff_ss


class BaseSubstitution(BaseSalary):
    title = "Calculo Base para substituição"
    description = """
        Este cálculo pode ser usado como base para substituições em geral.
    """
    MULTI_CALCULATE = True

    def get_substitutions(self):
        return (
            SubstitutionMovement.objects.filter(servidor=self.employee)
            .exclude(
                Q(data_fim__lt=self.range_salary.first)
                | Q(data_inicio__gt=self.range_salary.last)
            )
            .filter(posse__quadro__cargo__tipo_lei_cargo__in=["CM", "FC", "EL"])
        )

    @cache_return
    def _get_query(self):
        query = self.get_substitutions()

        if "oIds" in self.params:
            query = query.filter(pk__in=self.params.get("oIds"))
        else:
            q_exclude = Entry.objects.filter(
                contracheque__servidor=self.employee,
                contracheque__folha=self.reference_payroll,
                evento=self.event,
            )
            if self.entry:
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def extract_salaries_substitution(self):
        log.debug("RECALCULATE: OBJ %s" % self.object)

        base = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
        }
        if self.object:
            cache_id = "CBSUB%s%s" % (self.identification_payroll, self.object.pk)

            ranges_ = []

            log.debug(
                "SALARIES SUBSTITUION: (%s)%s - %s:%s"
                % (
                    self.object.posse.quadro.cargo.pk,
                    self.object.posse.quadro.cargo,
                    self.object.data_inicio,
                    self.object.data_fim,
                )
            )
            salaries_substitution = EstruturaTabelaSalarial.salarios(
                self.object.posse.quadro.cargo,
                self.object.data_inicio,
                self.object.data_fim,
            )

            for salary_sub in salaries_substitution:
                salaries = self.extract_base_salary_by_period()
                for salary in salaries:
                    log.debug(
                        "RECALCULATE: DRs %s : SALARY SUB %s: SALARY: %s"
                        % (
                            salary,
                            salary_sub[0],
                            NewDateRange.fromordinals(salary["range"]),
                        )
                    )
                    dr = NewDateRange.fromordinals(salary["range"]).intersect(
                        salary_sub[0]
                    )
                    if dr.days > 0:
                        # factor = dr.days / float(range_.days)
                        ef_ = salary.get("EF", salary.get("AC", base))
                        fc_ = salary.get("FC", base)
                        cm_ = salary.get("CM", salary.get("EL", base))
                        base_value = (
                            (ef_["base_value"] + ef_["extra"])
                            if (ef_["base_value"] + ef_["extra"]) > cm_["base_value"]
                            else cm_["base_value"]
                        )
                        # base_value *= factor
                        base_gratification = (
                            cm_["base_gratification"] + fc_["base_gratification"]
                        )  # * factor
                        value = float(salary_sub[1].valor) - base_value
                        gratification = (
                            float(salary_sub[1].gratificacao) - base_gratification
                        )
                        log.debug(
                            "%s BV: %s BG: %s V: %s G: %s"
                            % (
                                dr,
                                value,
                                gratification,
                                salary_sub[1].valor,
                                salary_sub[1].gratificacao,
                            )
                        )
                        config = {
                            "range": dr.toordinals(),
                            "EF": ef_,
                            "FC": fc_,
                            "CM": cm_,
                            "CMSUB": salary_sub[1],
                            "base_value": value if value > 0.00 else 0.00,
                            "base_gratification": gratification,  # if gratification > 0.00 else 0.00,
                        }
                        log.debug("CONFIG: %s" % config)
                        ranges_.append(config)

            set_cache(cache_id, ranges_, self.group_key_cache)

            return ranges_
        else:
            return {}

    @property
    @cache_return
    def range_substitution(self):
        range_ = NewDateRange()
        for config in self.extract_salaries_substitution():
            log.debug(
                "RANGE SUBSTITUION: %s" % NewDateRange.fromordinals(config["range"])
            )
            range_ += NewDateRange.fromordinals(config["range"])
        log.debug("RECALCULATE ESS: %s" % range_.days)
        return range_
        # return self.range_salary.intersect(NewDateRange(self.object.data_inicio, self.object.data_fim))

    def quantity(self):
        return (
            self.base_days
            if self.range_salary == self.range_substitution
            else self.range_substitution.days
        )

    def base_socialsecurity(self):
        return self.value()

    def event_information(self):
        return (
            (
                "%s ID%06d"
                % (
                    self.object.publicacao_alteracao
                    or self.object.publicacao_movimentacao,
                    self.object.pk,
                )
            )
            if self.object
            else ""
        )

    def unicode_for_obj(self, obj):
        return obj


class BaseCumulation(BaseSubstitution):
    title = "Calculo base para cumulação por substituição"
    description = """
        Este cálculo pode ser usado como base para substituições em geral.
    """
    MULTI_CALCULATE = True

    def get_substitutions(self):
        return (
            SubstitutionMovement.objects.filter(servidor=self.employee)
            .exclude(
                Q(data_fim__lt=self.range_salary.first)
                | Q(data_inicio__gt=self.range_salary.last)
            )
            .filter(
                posse__quadro__cargo__tipo_lei_cargo="EF",
                posse__quadro__cargo__indicativo="M",
            )
        )

    def extract_salaries_substitution(self):
        log.debug("RECALCULATE: OBJ %s" % self.object)

        base = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
        }
        if self.object:
            substitute_possession = self.get_possessions_by_type(["EF"]).filter(
                quadro__cargo__indicativo="M"
            )[0]
            if (
                substitute_possession.quadro.cargo.entrancia > 0
                and substitute_possession.quadro.cargo.entrancia
                < self.object.posse.quadro.cargo.entrancia
            ):
                if (
                    hasattr(self.employee, "_cache_diffs_substitution_by_periods")
                    and self.identification_payroll
                    in self.employee._cache_diffs_substitution_by_periods
                    and self.object.pk
                    in self.employee._cache_diffs_substitution_by_periods[
                        self.identification_payroll
                    ]
                ):
                    return self.employee._cache_diffs_substitution_by_periods[
                        self.identification_payroll
                    ][self.object.pk]

                ranges_ = {}

                log.debug(
                    "SALARIES SUBSTITUION: (%s)%s - %s:%s"
                    % (
                        self.object.posse.quadro.cargo.pk,
                        self.object.posse.quadro.cargo,
                        self.object.data_inicio,
                        self.object.data_fim,
                    )
                )
                salaries_substitution = EstruturaTabelaSalarial.salarios(
                    self.object.posse.quadro.cargo,
                    self.object.data_inicio,
                    self.object.data_fim,
                )
                for salary_sub in salaries_substitution:
                    salaries = self.extract_base_salary_by_period()
                    for salary in salaries:
                        log.debug("RECALCULATE: DRs %s : %s" % (salary, salary_sub[0]))
                        dr = NewDateRange.fromordinals(salary).intersect(salary_sub[0])
                        if dr.days > 0:
                            # factor = dr.days / float(range_.days)
                            ef_ = salary.get("EF", salary.get("AC", base))
                            fc_ = salary.get("FC", base)
                            cm_ = salary.get("CM", salary.get("EL", base))
                            base_value = ef_["base_value"]
                            # base_value *= factor
                            # base_gratification = 0.00
                            value = float(salary_sub[1].valor) - base_value
                            gratification = 0.00
                            log.debug(
                                "%s BV: %s BG: %s V: %s G: %s"
                                % (
                                    dr,
                                    value,
                                    gratification,
                                    salary_sub[1].valor,
                                    salary_sub[1].gratificacao,
                                )
                            )
                            config = {
                                "EF": ef_,
                                "FC": fc_,
                                "CM": cm_,
                                "CMSUB": salary_sub[1],
                                "base_value": value,
                                "base_gratification": gratification,
                            }
                            log.debug("CONFIG: %s" % config)
                            ranges_[dr] = config
                if not (hasattr(self.employee, "_cache_diffs_substitution_by_periods")):
                    self.employee._cache_diffs_substitution_by_periods = {}
                if (
                    self.identification_payroll
                    not in self.employee._cache_diffs_substitution_by_periods
                ):
                    self.employee._cache_diffs_substitution_by_periods[
                        self.identification_payroll
                    ] = {}

                self.employee._cache_diffs_substitution_by_periods[
                    self.identification_payroll
                ][self.object.pk] = ranges_
                return self.employee._cache_diffs_substitution_by_periods[
                    self.identification_payroll
                ][self.object.pk]
            else:
                return {}
        else:
            return {}

    @property
    @cache_return
    def range_substitution(self):
        range_ = NewDateRange()
        for dr in list(self.extract_salaries_substitution().keys()):
            range_ += dr
        log.debug("RECALCULATE: %s" % range_.days)
        return range_
        # return self.range_salary.intersect(NewDateRange(self.object.data_inicio, self.object.data_fim))

    def quantity(self):
        return (
            self.base_days
            if self.range_salary == self.range_substitution
            else self.range_substitution.days
        )

    def base_socialsecurity(self):
        return self.value()

    def event_information(self):
        return (
            (
                "%s ID%06d"
                % (
                    self.object.publicacao_alteracao
                    or self.object.publicacao_movimentacao,
                    self.object.pk,
                )
            )
            if self.object
            else ""
        )

    def unicode_for_obj(self, obj):
        return obj

    def base_value(self):
        base_value = 0.0
        days = 0.0
        ranges = self.extract_salaries_substitution()
        for range_ in ranges:
            base_value += ranges[range_].get("base_value", 0.00) * range_.days
            days += range_.days

        return (base_value / days) if days else 0.0


@RunCodeManager.register("gfp-classcodes-cumulation")
class Cumulation(SalaryEffective):
    title = "Cálculo de porcetagem de cumulação para membros"

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "qnt", "pct"]

    MULTI_CALCULATE = False
    JOIN_ON_MULTI = False

    @cache_return
    def quantity(self):
        if self.event:
            if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
                return float(self.params["qnt"] or 0)
            if self.event.quantity_at(self.range_salary.first) is not None:
                return float(self.event.quantity_at(self.range_salary.first))
        return 0

    @cache_return
    def event_information(self):
        if "info" in self.params:
            return self.params["info"]
        return ""


@RunCodeManager.register("gfp-classcodes-substituion-efective")
class EfectiveSubstitution(BaseSubstitution):
    title = "Calculo Substituição de Efetivos."
    description = """
        Calculo retorna toda a diferença de substituição (vencimento/gratificação) juntos.
        Esse método é usualmente utilizado no MP-TO, mas está sendo revisto para que a diferença de
        vencimento seja retornada separada da diferença de gratificação, sendo assim, necessitará de
        2 rubricas/eventos diferentes.
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += (
                config.get("base_value", 0.00) + config.get("base_gratification", 0.00)
            ) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-classcodes-substituion-complement")
class ComplementSubstitution(BaseSubstitution):
    title = "Complemento de substituição para a remuneração"
    description = """
        Calculo retorna o complemento entre a remuneração do servidor e o salário do cargo a ser substituído!
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        # log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += (
                config.get("base_value", 0.00) + config.get("base_gratification", 0.00)
            ) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-classcodes-substituion-complement-member")
class ComplementSubstitutionMember(ComplementSubstitution):
    title = "Complemento de substituição para membros"
    description = """
        Calculo retorna o complemento entre o subsídio do membro substituído e do substituto!
    """

    def __init__(self, employee, payroll, event=None, **kwargs):
        super(ComplementSubstitutionMember, self).__init__(
            employee, payroll, event=None, **kwargs
        )
        self.possession_substitute = (
            self.employee.get_posses_ativas(
                self.range_salary.first, self.range_salary.last
            )
            .filter(
                servidor__tipo="M",
                quadro__cargo__tipo_lei_cargo="EF",
                quadro__cargo__level_instance__in=[1, 2, 3],
            )
            .first()
        )

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            not self.employee.tipo == "M"
            or not self.possession_substitute
            or self.possession_substitute.quadro.cargo.level_instance is None
        ):
            raise self.CalculationNotApplicable(
                "O Servidor precisa ser membro já titularizado de 1ª instância!"
            )

    def get_substitutions(self):
        # TODO: RAIENE - VERIFICAR, acho que é necessário modificar implementação
        # TODO: OBSERVAR RELAÇÃO COM CARGO E CONFIG
        return SubstitutionMovement.objects.exclude(
            Q(data_fim__lt=self.range_salary.first)
            | Q(data_inicio__gt=self.range_salary.last)
        ).filter(
            Q(servidor=self.employee)
            & Q(posse__quadro__cargo__tipo_lei_cargo__in=["EF"])
            & Q(servidor__tipo="M")
            & Q(servidor_substituido__tipo="M")
            & Q(
                Q(posse__quadro__cargo__level_instance__in=[2, 3])
                | Q(posse__quadro__cargo__instance=2)
            )
            & Q(
                Q(
                    posse__quadro__cargo__level_instance__gt=self.possession_substitute.quadro.cargo.level_instance
                )
                | Q(posse__quadro__cargo__instance=2)
            )
        )

    @cache_return
    def _get_query(self):
        query = self.get_substitutions()

        if "oIds" in self.params:
            query = query.filter(pk__in=self.params.get("oIds"))
        else:
            q_exclude = Entry.objects.filter(
                contracheque__servidor=self.employee,
                contracheque__folha=self.reference_payroll,
                evento=self.event,
            )
            if self.entry:
                log.debug("%s:%s" % (self.entry, q_exclude))
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def extract_salaries_substitution(self):
        log.debug("RECALCULATE: OBJ %s" % self.object)

        base = {
            "base_gratification": 0.0,
            "base_value": 0.0,
            "days": 0,
            "gratification": 0.0,
            "reference": None,
            "value": 0.0,
            "full_base_socialsecurity": 0.0,
            "base_socialsecurity": 0.0,
            "extra": 0.0,
            "base_extra": 0.0,
        }
        if self.object:
            cache_id = "CBSUBM%s%s" % (self.identification_payroll, self.object.pk)

            ranges_ = []

            log.debug(
                "SALARIES SUBSTITUION: (%s)%s - %s:%s"
                % (
                    self.object.posse.quadro.cargo.pk,
                    self.object.posse.quadro.cargo,
                    self.object.data_inicio,
                    self.object.data_fim,
                )
            )
            salaries_substitution = EstruturaTabelaSalarial.salarios(
                self.object.posse.quadro.cargo,
                self.object.data_inicio,
                self.object.data_fim,
            )

            for salary_sub in salaries_substitution:
                salaries = self.extract_base_salary_by_period()
                for salary in salaries:
                    log.debug(
                        "RECALCULATE: DRs %s : SALARY SUB %s: SALARY: %s"
                        % (
                            salary,
                            salary_sub[0],
                            NewDateRange.fromordinals(salary["range"]),
                        )
                    )
                    dr = NewDateRange.fromordinals(salary["range"]).intersect(
                        salary_sub[0]
                    )
                    if dr.days > 0:
                        # factor = dr.days / float(range_.days)
                        ef_ = salary.get("EF", base)
                        fc_ = base
                        cm_ = base
                        base_value = ef_["base_value"]
                        value = float(salary_sub[1].valor) - base_value
                        gratification = 0
                        log.debug(
                            "%s BV: %s BG: %s V: %s G: %s"
                            % (
                                dr,
                                value,
                                gratification,
                                salary_sub[1].valor,
                                salary_sub[1].gratificacao,
                            )
                        )
                        config = {
                            "range": dr.toordinals(),
                            "EF": ef_,
                            "FC": fc_,
                            "CM": cm_,
                            "CMSUB": salary_sub[1],
                            "base_value": value if value > 0.00 else 0.00,
                            "base_gratification": (
                                gratification if gratification > 0.00 else 0.00
                            ),
                        }
                        log.debug("CONFIG: %s" % config)
                        ranges_.append(config)

            set_cache(cache_id, ranges_, self.group_key_cache)

            return ranges_
        else:
            return {}

    def event_information(self):
        return (
            ("%s ID%06d" % (self.object.posse.quadro.cargo, self.object.pk))
            if self.object
            else ""
        )


@RunCodeManager.register("gfp-classcodes-substituion-salary")
class CommissionedSubstitution(BaseSubstitution):
    title = "Calculo Substituição para a parte vencimental da remuneração."
    description = """
        Calculo retorna o complemento da parte vencimental do cargo comissionado do substituído.
        Lembrando que se o servidor possui subsídio/vencimento + vpi maior que o vencimento do cargo,
        o calculo retornará zerado (0,00), pois não há o que complementar na parte vencimental
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += config.get("base_value", 0.00) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


@RunCodeManager.register("gfp-classcodes-substituion-gratification")
class GratificationSubstitution(BaseSubstitution):
    title = "Calculo Substituição para a parte vencimental da remuneração."
    description = """
        Calculo retorna o complemento da parte vencimental do cargo comissionado do substituído.
        Lembrando que se o servidor possui subsídio/vencimento + vpi maior que o vencimento do cargo,
        o calculo retornará zerado (0,00), pois não há o que complementar na parte vencimental
    """
    JOIN_ON_MULTI = False

    def base_value(self):
        base_value = 0.0
        days = 0.0
        configs = self.extract_salaries_substitution()
        log.debug(configs)
        for config in configs:
            dr = NewDateRange.fromordinals(config["range"])
            base_value += config.get("base_gratification", 0.00) * dr.days
            days += dr.days

        return (base_value / days) if days and base_value > 0.00 else 0.00


class BaseChristmasGratification(BaseSalary):

    title = "Base para os cálculos de 13° Salário"

    FULL_VALUE = True

    FIELD_RETURN_TO_BASE_VALUE = "valor_base"

    @property
    def references(self):
        return (self.range_salary.first.year, 13)

    def configure(self):
        range_indemnity = NewDateRange(date(2016, 1, 1), date(2017, 8, 31))
        dt = date(self.range_salary.first.year, self.range_salary.first.month, 1)
        if self.object and range_indemnity.in_range(dt):
            self.EXCLUDE_SALARIES_BY_TYPE_AND_JOB = {"M": ["CM", "EL"]}

    @property
    @cache_return
    def range_13salary(self):
        range_year = NewDateRange(
            datetime(self.year, 1, 1), datetime(self.year, 12, 31)
        )
        return self.range_salary_for(range_salary=range_year)

    def maximum_quantity(self):
        return 12.00

    @cache_return
    def quantity(self):
        range_period = self.range_13salary
        qtd = 0
        for month in range(12):
            range_month = range_period.intersect(
                NewDateRange.from_month(self.year, month + 1)
            )
            if range_month.days >= 15:
                qtd += 1

        return qtd

    def base_socialsecurity(self):
        log.debug(self._base_values())
        return self._base_values()[1] * self.factor_quantity()

    def _get_bases(self):
        base = self.new_base_salary()
        log.debug(base)
        log.debug(base["base_value"])
        log.debug(base["base_gratification"])
        if self.full_value and base["days"] == self.quantity:
            total_base = (
                base["base_value"] + base["base_gratification"]
            )  # + base['base_extra']
        else:
            total_base = base["value"] + base["gratification"]
        total_base_socialsecurity = base["full_base_socialsecurity"]
        log.debug(
            "BASE_SALARY (%s) >>>> VALUE: %s FBSS: %s BASE_GRAT: %s FQ: %s"
            % (
                self.factor_quantity(),
                total_base,
                base["full_base_socialsecurity"],
                total_base_socialsecurity,
                self.factor_quantity(),
            )
        )
        return total_base, total_base_socialsecurity, self.quantity, 0


@RunCodeManager.register("gfp-classcodes-13thsalary")
class ChristmasGratification(BaseChristmasGratification):

    title = "13° Salário"

    def base_value_query(self):
        # q_entries = Q(
        #     evento__numero__in=self.focuses_on,
        #     contracheque__servidor=self.employee,
        #     contracheque__pensioner=self.pensioner,
        # )
        # '''
        # CALCULATE_OVER
        # Indica sobre quais lancamentos o base_value_query incidira:
        # 1: Calcular sobre lancamentos dentro do próprio contracheque
        # 2: Calcular sobre lancamentos do mesmo periodo do contracheque
        # 3: Calcular sobre lancamentos de mesma referencia do calculo
        # '''

        # if self.CALCULATE_OVER == 2 or self.ALL_PAYROLL:
        #     q_entries = (
        #         Q(contracheque__folha__periodo=self.reference_payroll.periodo) & q_entries)
        # elif self.CALCULATE_OVER == 3:
        #     q_entries = (
        #         Q(reference_year=self.references[0], reference_month=self.references[1]) & q_entries)
        # if self.CALCULATE_OVER == 1:
        #     q_entries = (Q(contracheque__folha=self.payroll) & q_entries)

        # if self.exclude_events:
        #     q_entries = Q(q_entries & ~Q(
        #         evento__numero__in=self.exclude_events))
        # if self.only_events:
        #     q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))
        # # log.debug(q_entries)
        # # log.debug(Entry.objects.filter(q_entries).order_by(
        # #     'evento__order', 'evento__numero'))
        # return Entry.objects.filter(q_entries).order_by('evento__order', 'evento__numero')

        q_ = Q(
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

        def resolve_queries(CALCULATE_OVER):
            if CALCULATE_OVER == 2 or self.ALL_PAYROLL:
                return Q(contracheque__folha__periodo=self.reference_payroll.periodo)
            elif CALCULATE_OVER == 3:
                # log.debug('E TRES E CALA BOCA')
                return Q(
                    reference_year=self.references[0],
                    reference_month=self.references[1],
                )
            if CALCULATE_OVER == 1:
                return Q(contracheque__folha=self.payroll)

        q_entries = resolve_queries(self.CALCULATE_OVER) & q_
        if self.CALCULATE_OVER == 3:
            if not Entry.objects.filter(q_entries).exists():
                q_entries = resolve_queries(1) & q_
        if self.exclude_events:
            q_entries = Q(q_entries & ~Q(evento__numero__in=self.exclude_events))
        if self.only_events:
            q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))
        return Entry.objects.filter(q_entries).order_by(
            "evento__order", "evento__numero"
        )

    def extract_salaries_by_period(self, period=None):
        base_period = Periodo.objects.filter(
            mes=12, ano=self.payroll.periodo.ano
        ).last()
        retorno_com_period = super(
            ChristmasGratification, self
        ).extract_salaries_by_period(base_period)
        log.debug(retorno_com_period)
        return retorno_com_period

    def value(self):
        log.debug(self._get_bases())
        return super(WorkDaysCalculation, self).value()


@RunCodeManager.register("gfp-classcodes-Advance13thsalary")
class AdvanceChristmasGratification(BaseChristmasGratification):

    title = "Adiantamento de 13° Salário"

    def percentage(self):
        return 50.0000

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.payroll.periodo.mes == 13:
            raise self.MonthNotValid()

        year = (
            self.payroll.periodo.ano
            if self.payroll.periodo.mes < 12
            else self.payroll.periodo.ano + 1
        )
        q1 = Q(contracheque__folha__periodo__ano=year) & Q(
            contracheque__folha__periodo__mes__range=[1, 11]
        )
        q2 = Q(contracheque__folha__periodo__ano=year - 1) & Q(
            contracheque__folha__periodo__mes=12
        )
        query = self.employee.entries.filter(
            (Q(evento=self.event) | Q(evento=self.event.previous_event)) & Q(q1 | q2)
        ).exclude(contracheque__folha=self.payroll)
        if query.exists():
            raise self.CalculationNotApplicable(
                "O servidor já possui adiantamento para o exercício %s" % year
            )

        valid_months = [
            6,
            max(self.employee.pessoa_fisica.data_nascimento.month - 1, 1),
        ]
        if self.payroll.periodo.mes not in valid_months:
            raise self.CalculationNotApplicable(
                "Apenas pode ser requerido no mês de junho ou anterior ao mês de aniversário!"
            )

    def base_socialsecurity(self):
        return self.value()


@RunCodeManager.register("gfp-classcodes-mpto-Advance13thsalary-13820182")
class AdvanceChristmasGratification1382018(AdvanceChristmasGratification):

    title = "Adiantamento de 13° Salário - Ato 138/2018"

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.payroll.periodo.mes == 13:
            raise self.MonthNotValid()

        year = (
            self.payroll.periodo.ano
            if self.payroll.periodo.mes < 12
            else self.payroll.periodo.ano + 1
        )
        q1 = Q(contracheque__folha__periodo__ano=year) & Q(
            contracheque__folha__periodo__mes__range=[1, 11]
        )
        q2 = Q(contracheque__folha__periodo__ano=year - 1) & Q(
            contracheque__folha__periodo__mes=12
        )
        query = self.employee.entries.filter(
            (Q(evento=self.event) | Q(evento=self.event.previous_event))
            & Q(q1 | q2)
            & Q(status="CT")
        ).exclude(contracheque__folha=self.payroll)
        # log.debug(query)
        if query.exists():
            raise self.CalculationNotApplicable(
                "O servidor já possui adiantamento para o exercício %s" % year
            )


@RunCodeManager.register("gfp-classcodes-DevolutionAdvance13thsalary")
class DevolutionAdvanceChristmasGratification(BaseCalculation):
    titulo = "Desconto devido adiantamento de 13° Salário"

    MULTI_CALCULATE = True
    JOIN_ON_MULTI = False

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.month in [12]:
            raise self.CalculationNotApplicable(
                "A devolução de adiantamento de 13º não deve ser cobrado em dezembro! Utilize a folha do 13º."
            )

    @property
    @cache_return
    def query_advances(self):
        q1 = Q(
            Q(folha__periodo__ano=self.payroll.periodo.ano)
            & Q(folha__periodo__mes__range=[1, 11])
        )
        q2 = Q(
            Q(folha__periodo__ano=self.payroll.periodo.ano - 1)
            & Q(folha__periodo__mes=12)
        )

        return self.employee.entries.filter(
            Q(evento__numero__in=self.focuses_on) & Q(q1 | q2)
        )

    @cache_return
    def _get_query(self):
        query = self.query_advances

        if "oIds" in self.params:
            query = query.filter(pk__in=self.params.get("oIds"))
        else:
            q_exclude = Entry.objects.filter(
                contracheque__servidor=self.employee,
                contracheque__folha=self.payroll,
                evento=self.event,
            )
            if self.entry:
                # log.debug(u'%s:%s' % (self.entry, q_exclude))
                q_exclude = q_exclude.exclude(pk=self.entry.pk)
            exclude_ids = []
            for e in q_exclude:
                for id_ in e.oIds or []:
                    exclude_ids.append(id_)

            query = query.exclude(pk__in=exclude_ids)

        return query

    def quantity(self):
        return self.query_advances.count()

    def maximum_quantity(self):
        return 1.00

    def base_value(self):
        if self.object:
            return float(self.object.valor)
        return 0.00

    @property
    def references(self):
        if self.object:
            return (
                self.object.contracheque.folha.periodo.ano,
                self.object.contracheque.folha.periodo.mes,
            )
        return (self.year, self.month)

    def unicode_for_obj(self, obj):
        return "%02d/%04d (%s)" % (obj.reference_month, obj.reference_year, obj.evento)


@RunCodeManager.register("gfp-classcodes-rescission-13thsalary")
class ChristmasGratificationRescission(ChristmasGratification):

    title = "13° proporcional"

    def __init__(self, employee, payroll, event, entry=None, cid=None, **kwargs):
        if employee.data_desligamento:
            kwargs["month"] = (employee.data_desligamento - relativedelta(days=1)).month
        super(ChristmasGratificationRescission, self).__init__(
            employee, payroll, event, entry, cid, **kwargs
        )

    def validate(self):
        self.validate_not_paycheck_pension()
        if (
            self.employee.data_desligamento
            and self.month != self.employee.data_desligamento.month
            and self.year != self.employee.data_desligamento.year
        ):
            raise self.CalculationNotApplicable(
                "13º proporcional não pode ser pago em mês diferente do desligamento."
            )
        if self.employee.situacao_funcional_cache not in [
            "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
            "ATIVO_LIC_INTERESSE",
        ]:
            if (
                not self.employee.data_desligamento
                and not self.employee.get_afastamentos(
                    self.range_salary.first, self.range_salary.last
                ).filter(
                    baselicencaafastamento__estado__in=[1, 2, 3],
                    baselicencaafastamento__tipo__in=[14, 18],
                )
            ):
                raise self.CalculationNotApplicable(
                    "O Servidor %s não está desligado" % (self.employee)
                )
        if self.month in [12, 13]:
            raise self.CalculationNotApplicable(
                "13º proporcional não deve ser pago em dezembro! Para isso utilize a folha do 13º."
            )

    def _get_value_from_calc(self, calc, full_value=False):
        return calc.value() if not calc.full_value else calc.valor_base()

    def _get_value_from_entry(self, entry):
        return float(entry.correct_valor if self.full_value else entry.valor_base)

    @property
    def ceiling(self):
        return (
            float(self.payroll.periodo.salario_teto_membros or 999999.99)
            if self.employee.tipo == "M"
            else float(self.payroll.periodo.salario_teto_adm or 999999.99)
        )

    def value(self):
        value = super(ChristmasGratificationRescission, self).value()
        if value:
            value = min(value, self.ceiling)
        return value

    @property
    @cache_return
    def range_13salary(self):
        range_year = NewDateRange(
            datetime(self.year, 1, 1),
            datetime(self.year, self.month, self.range_salary.last.day),
        )
        log.debug(range_year)
        log.debug(self.range_salary_for(range_salary=range_year))
        return self.range_salary_for(range_salary=range_year)

    @property
    def references(self):
        return (self.year, 13)

    def base_socialsecurity(self):
        base = super(ChristmasGratificationRescission, self).base_socialsecurity()
        if base:
            base = min(base, self.ceiling)
        return base
