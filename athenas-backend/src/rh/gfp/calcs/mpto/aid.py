# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Q
from memoization import cached
from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.calcs.mpto.base import WorkDaysCalculation
from rh.gfp.models import ExtraPaymentPeriod, FolhaEvento, FamilySalary
from rh.models import Comarca, Dependencia
from standard.models import RunCodeManager

log = getLogger(__name__)


class AidExtraPaymentBaseExtraPayment(WorkDaysCalculation):

    MULTI_CALCULATE = True

    SLUG_EXTRA_PAYMENT_FOR_AID = ""

    FILTER_EMPLOYEE = False

    FULL_VALUE = True

    FILTER_BY_TYPE = None

    WITHOUT_DAYS = False

    def validate(self):
        self.validate_not_paycheck_pension()
        if not self.get_query():
            txt = "O servidor %s não possui pagamento configurado para %s" % (
                self.employee,
                self.SLUG_EXTRA_PAYMENT_FOR_AID,
            )
            raise self.CalculationNotApplicable(txt)

    @property
    def range_query_extra(self):
        return self.payroll.date_range

    def _query_extra_payments(self):
        slugs = (
            self.SLUG_EXTRA_PAYMENT_FOR_AID
            if isinstance(self.SLUG_EXTRA_PAYMENT_FOR_AID, tuple)
            else (self.SLUG_EXTRA_PAYMENT_FOR_AID,)
        )
        q = ExtraPaymentPeriod.objects.filter(extra_payment__slug__in=slugs).filter(
            models.Q(start_validity__lte=self.range_query_extra.last)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.range_query_extra.first)
            )
        )
        if self.FILTER_EMPLOYEE:
            q = q.filter(employee=self.employee)

        if self.FILTER_BY_TYPE:
            q = q.filter(type_value=self.FILTER_BY_TYPE)

        return q

    def base_value(self):

        if self.object and self.object.type_value == 2:
            value = super().base_value()
        else:
            # q = self._query_extra_payments()
            value = float(self.object.value)  # if q.exists() else 0.00

        return round(value, 2)

    def _filter_repeated_cid(self):
        return self._get_query()

    def _get_query(self):
        query = self._query_extra_payments()
        # log.debug(self.params)

        if "oIds" in self.params and self.params["oIds"]:
            query = query.filter(pk__in=self.params["oIds"])

        return query

    def percentage(self):
        if self.object and self.object.type_value == 2:
            return self.object.value
        return super().percentage()

    @cached()
    def quantity_13(self):
        # vai pro base salary; avaliar self._is_christmas_grat
        range_period = self.range_13salary
        qtd = 0
        for month in range(12):
            range_month = range_period.intersect(
                NewDateRange.from_month(self.year, month + 1)
            )
            if range_month.days >= 15:
                qtd += 1

        return qtd

    def quantity(self):
        if self.WITHOUT_DAYS:
            return self.maximum_quantity()
        elif self.object:
            return (
                self.days_quantity(self.object)
                if not self._is_christmas_grat
                else self.quantity_13()
            )
        return 0

    def days_quantity(self, obj):
        range_salary = self.range_salary_for().intersect(
            NewDateRange(obj.start_validity, obj.end_validity)
        )
        return range_salary.days

    def event_information(self):
        if self.object:
            return "%s" % (
                self.object.information if self.object.information else self.object.id
            )
        else:
            return ""

    def unicode_for_obj(self, obj):
        return (
            (
                "%s - R$ %s"
                % (
                    obj.start_validity.strftime("%d-%m-%Y"),
                    (("%s%%" if obj.type_value == 2 else "R$ %s") % obj.value),
                )
            )
            if obj
            else ""
        )


class AidExtraPaymentBaseDependence(WorkDaysCalculation):

    MULTI_CALCULATE = True

    SLUG_EXTRA_PAYMENT_FOR_AID = ""

    TYPE_AID = 0

    def days(self):
        return self.base_days - (
            self.payroll.date_range.days - self.range_salary_for().days
        )

    def validate(self):
        self.validate_not_paycheck_pension()
        if not self.get_query():
            txt = (
                "O servidor %s não possui depedentes para o auxílio creche para a folha %s"
                % (self.employee, self.payroll)
            )
            raise self.CalculationNotApplicable(txt)

    def base_value(self):

        q = ExtraPaymentPeriod.objects.filter(
            extra_payment__slug=self.SLUG_EXTRA_PAYMENT_FOR_AID
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return round(float(q[0].value), 2) if q.exists() else 0.00

    def quantity(self):
        if self.object:
            return self.days_quantity(self.object)
        return 0

    def days_quantity(self, dependence):
        range_salary = self.range_salary_for().intersect(
            NewDateRange(
                dependence.data_inicio,
                dependence.data_fim if dependence.data_fim else None,
            )
        )
        return range_salary.days

    def _get_query(self):
        query = Dependencia.objects.filter(
            models.Q(
                tipo=self.TYPE_AID,  # IMPOSTO DE RENDA
                suspenso=False,
                data_inicio__lte=self.payroll.date_range.last,
                dependente__servidor=self.employee,
                dependente__grau_parentesco__in=(3, 4, 5, 6, 7, 9),
            )
            & (
                models.Q(data_fim=None)
                | models.Q(data_fim__gte=self.payroll.date_range.first)
            )
        )

        if "oIds" in self.params and self.params["oIds"]:
            query = query.filter(pk__in=self.params["oIds"])

        return query

    def event_information(self):
        return self.object.dependente.pessoa_fisica.abbreviation

    def unicode_for_obj(self, obj):
        return obj.dependente.pessoa_fisica.abbreviation if obj else ""


class AidExtraPaymentPercent(AidExtraPaymentBaseExtraPayment):

    title = "Cálculo de Verbas adicionais por Percentual"

    MULTI_CALCULATE = True

    @cached()
    def percentage(self):
        if self.object:
            return round(self.object.value, 2)
        else:
            return 0


@RunCodeManager.register("gfp-mpto-aid-supply")
class AidSupply(WorkDaysCalculation):

    title = "Cálculo do Auxílio Alimentação"
    EXCLUDE_BY_JOB = [
        "AC",
    ]

    def maximum_quantity(self):
        return 22.0

    @cached()
    def quantity(self):
        work_days_of_month = self.range_salary.work_days
        worked_days_of_month = self.range_salary_for().work_days
        qtd_max = self.maximum_quantity()
        if worked_days_of_month == 0:
            return worked_days_of_month

        if work_days_of_month == worked_days_of_month:
            days = qtd_max
        else:
            days = worked_days_of_month

        return days if days < qtd_max else qtd_max

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        range_ = super(AidSupply, self)._exclude_ranges_for_range_salary(
            range_salary=range_salary
        )
        q = (
            self.employee.departures(
                self.payroll.periodo.range.first, self.payroll.periodo.range.last
            )
            .filter(
                Q(tipo__in=[11, 14, 15, 16, 18, 21, 22, 23, 29, 44])
                # Q(tipo__in=[11, 14, 15, 16, 18, 21, 29])
            )
            .filter(~Q(afastamento__afastamentooutroorgao__transito_pela_folha=True))
            .exclude(
                # Excluindo os membros que estão afastado por processo disciplinar (44), pois os mesmos não podems ser
                # punidos de acordo com Art. 202 da Lei 51/2008
                Q(tipo=44)
                & Q(servidor__tipo="M")
            )
        )

        for absence in q.exclude(tipo=11):
            range_ += NewDateRange(absence.data_inicio, absence.data_fim)

        for absence in q.filter(tipo=11):  # Licença Doença Pessoa na Familia > 3 meses
            dt_start = absence.data_inicio + relativedelta(months=3)
            if dt_start <= absence.data_fim:
                range_ += NewDateRange(dt_start, absence.data_fim)

        # log.debug('RANGE LICENSES: %s' % range_)

        return range_

    def base_value(self):
        q = ExtraPaymentPeriod.objects.filter(
            extra_payment__slug="AUXILIO-ALIMENTACAO"
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return round(float(q[0].value), 2) if q.exists() else 0.00


@RunCodeManager.register("gfp-mpto-aid-supply-ii")
class AidSupplyII(AidSupply):

    def _exclude_ranges_for_range_salary(self, range_salary=None):
        range_ = super(AidSupply, self)._exclude_ranges_for_range_salary(
            range_salary=range_salary
        )

        tipos = [11, 14, 15, 16, 18, 21, 22, 23, 29, 44]
        if self.employee.type_by_possession in ["MBR", "MEL", "MCM", "MEC"]:
            tipos.append(62)

        q = (
            self.employee.departures(self.range_salary.first, self.range_salary.last)
            .filter(Q(tipo__in=tipos))
            .filter(~Q(afastamento__afastamentooutroorgao__transito_pela_folha=True))
        )

        if 62 not in tipos and self.employee.tipo != "M":
            q = q.exclude(
                # Excluindo os membros que estão afastado por processo disciplinar (44), pois os mesmos não podems ser
                # punidos de acordo com Art. 202 da Lei 51/2008
                Q(tipo=44)
                & Q(servidor__tipo="M")
            )

        for absence in q.exclude(tipo=11):
            range_ += NewDateRange(absence.data_inicio, absence.data_fim)

        for absence in q.filter(tipo=11):  # Licença Doença Pessoa na Familia > 3 meses
            dt_start = absence.data_inicio + relativedelta(months=3)
            if dt_start <= absence.data_fim:
                range_ += NewDateRange(dt_start, absence.data_fim)

        # log.debug('RANGE LICENSES: %s' % range_)

        return range_


@RunCodeManager.register("gfp-mpto-aid-supply-iii")
class AidSupplyIII(AidSupplyII):

    class AidRange(object):

        def __str__(self):
            return self.pk[4:6] + "/" + self.pk[:4]

    MULTI_CALCULATE = True

    def __init__(self, employee, payroll, event=None, **kwargs):
        super(AidSupplyIII, self).__init__(employee, payroll, event, **kwargs)
        # params = kwargs['params'] if 'params' in kwargs else None

        if self.params.get("oIds", []):
            oId = int(self.params["oIds"][0])
            self.year = self.payroll.periodo.ano
            self.month = (
                self.payroll.periodo.mes if oId == 1 else (self.payroll.periodo.mes + 1)
            )
            self.range_salary = NewDateRange.from_month(
                self.year, (self.month if self.month < 12 else 12)
            )
            self.validity = self.range_salary

    def get_query(self):

        # 1 - Mês da folha atual
        # 2 - Mês da folha subsequente

        aid_list = []

        q_paid = FolhaEvento.objects.filter(
            contracheque__servidor=self.employee,
            evento=self.event,
            reference_month=self.payroll.periodo.mes,
            reference_year=self.payroll.periodo.ano,
            contracheque__pensioner=None,
        )
        if self.entry:
            q_paid = q_paid.exclude(pk=self.entry.pk)

        # log.debug('GET_QUERY: %s %s' % (self.__class__.__name__, q_paid.count()))
        if not q_paid.exists():
            aid_list.append(1)

        if self.payroll.periodo.mes < 12:
            aid_list.append(2)

        if (
            "oIds" in self.params
            and self.params["oIds"]
            and self.params["oIds"][0] in aid_list
        ):
            aid_list = [self.params["oIds"][0]]

        return aid_list

    def validate(self):
        # for q in self.get_query():
        if self.object:
            month_temp = (
                self.payroll.periodo.mes
                if self.object == 1
                else (self.payroll.periodo.mes + 1)
            )
            year_temp = self.payroll.periodo.ano
            query = FolhaEvento.objects.filter(
                contracheque__servidor=self.employee,
                evento=self.event,
                reference_month=month_temp,
                reference_year=year_temp,
                contracheque__pensioner=None,
            )
            if self.entry:
                query = query.exclude(pk=self.entry.pk)
            if query.exists():
                raise self.CalculationNotApplicable(
                    "Referência %02d/%04d já paga" % (month_temp, year_temp)
                )

        if self.month < 8 and self.year <= 2018 or self.year < 2018:
            raise self.CalculationNotApplicable(
                "Cálculo não aplicado para periodo anterior a 08/2018"
            )
        if self.pensioner:
            raise self.CalculationNotApplicable(
                "Cálculo não aplicado para pensionistas"
            )

    def base_value(self):
        # log.debug('BASE_VALUE: %s %s' % (self.__class__.__name__, self.object))
        if self.object:
            return super(AidSupplyIII, self).base_value()
        return 0.0

    def unicode_for_obj(self, obj):
        text = "%04d%02d" % (
            self.payroll.periodo.ano,
            self.payroll.periodo.mes if obj == 1 else (self.payroll.periodo.mes + 1),
        )
        return text


@RunCodeManager.register("gfp-mpto-aid-daycare")
class AidDaycare(AidExtraPaymentBaseDependence):
    """
    Premissas para o cálculo:
    -ser dependente economico-financeiro;
    -dependente com idade menor que 6 anos
    """

    title = "Cálculo do Auxílio Creche"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUXILIO-CRECHE"

    TYPE_AID = 4

    FILTER_QUERY = 2
    FILTER_BY = 2

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.employee.tipo == "M":
            raise self.CalculationNotApplicable("Membro não tem direito a Aux. Creche!")


@RunCodeManager.register("gfp-mpto-aid-special")
class AidSpecial(AidExtraPaymentBaseDependence):
    """
    Premissas para o cálculo:
    -ser dependente economico-financeiro;
    -possuir alguma deficiencia
    """

    title = "Cálculo do Auxílio Especial"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUXILIO-ESPECIAL"

    TYPE_AID = 6

    FILTER_QUERY = 2
    FILTER_BY = 2


@RunCodeManager.register("gfp-mpto-aid-habitation")
class AidHabitation(WorkDaysCalculation):
    """
    Premissas para o cálculo:
    - Ser membro do mp
    """

    title = "Cálculo do Auxílio Moradia"

    MULTI_CALCULATE = True

    @cached()
    def get_possessions(self):
        possessions = (
            self.employee.posses.exclude(
                models.Q(data_exercicio__gt=self.payroll.date_range.last)
            )
            .filter(
                models.Q(desligamento=None)
                | models.Q(
                    desligamento__data_desligamento__gte=self.payroll.date_range.first
                )
            )
            .filter(
                models.Q(quadro__cargo__tipo_lei_cargo="EF")
                & models.Q(quadro__cargo__indicativo="M")
            )
            .order_by("-data_exercicio")
        )

        return possessions

    def validate(self):
        self.validate_not_paycheck_pension()
        if not (self.employee.is_promotor or self.employee.is_procurador):
            raise self.CalculationNotApplicable(
                "Cálculo aplicável apenas à membros do MP!"
            )

    def base_value(self):
        q = ExtraPaymentPeriod.objects.filter(
            extra_payment__slug="AUXILIO-MORADIA"
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return round(float(q[0].value), 2) if q.exists() else 0.00

    def quantity(self):
        if self.object:
            date_range = NewDateRange()
            for d in self.employee.servidor_lotacao.filter(
                lotacao__comarca=self.object
            ):
                _range = self.range_salary_for().intersect(
                    NewDateRange(
                        d.data_vigencia_inicio,
                        (d.data_vigencia_fim if d.data_vigencia_fim else None),
                    )
                )
                date_range += _range
                # log.debug('AID HABITATION: %s - %s' % (_range, d))
            return date_range.days

        return 0

    def _get_query(self):
        if self.params.get("oIds"):
            return Comarca.objects.filter(pk__in=self.params.get("oIds"))
        else:
            comarcas = set()
            query = self.employee.servidor_lotacao.exclude(
                data_vigencia_fim__lt=self.payroll.date_range.first
            ).filter(data_vigencia_inicio__lte=self.payroll.date_range.last)
            for row in query:
                comarcas.add(row.lotacao.comarca)
            comarcas = list(comarcas)

            return comarcas

    def event_information(self):
        return self.object


@RunCodeManager.register("gfp-mpto-aid-cumulation")
class AidCumulation(AidExtraPaymentPercent):

    PARAMS_ = ["info", "qnt", "pct", "oIds"]

    SLUG_EXTRA_PAYMENT_FOR_AID = "CUMULATION"
    FILTER_EMPLOYEE = True
    FULL_VALUE = False

    def configure(self):
        self.validity = NewDateRange(date(2016, 1, 1), date(2017, 8, 31))

    def maximum_quantity(self):
        return self.base_days

    def quantity_origin(self):
        if self.object:
            return self.days_quantity(self.object)
        return 0

    @cached()
    def quantity(self):
        if self.event:
            if "qnt" in self.params and (self.params["qnt"] or self.params["qnt"] == 0):
                return float(self.params["qnt"])
        return self.quantity_origin()

    @cached()
    def percentage(self):
        if "pct" in self.params and float(self.params["pct"] or 0) != 0.0:
            return float(self.params["pct"] or super(AidCumulation, self).percentage())
        return super(AidCumulation, self).percentage()

    @cached()
    def event_information(self):
        if "info" in self.params and self.params["info"] != "":
            return self.params["info"]
        return super(AidCumulation, self).event_information()


@RunCodeManager.register("gfp-mpto-urv-admin-employee")
class URVAdminEmployee(AidExtraPaymentPercent):

    PARAMS_ = ["oIds"]

    SLUG_EXTRA_PAYMENT_FOR_AID = "URV-ADMIN-EMPLOYEE"
    FILTER_EMPLOYEE = True
    FULL_VALUE = True

    @cached()
    def quantity_13(self):
        # vai pro base salary; avaliar self._is_christmas_grat
        range_period = self.range_13salary
        # log.debug(range_period)
        # log.debug(self._exclude_ranges_for_range_salary())
        qtd = 0
        for month in range(12):
            range_month = range_period.intersect(
                NewDateRange.from_month(self.year, month + 1)
            )
            if range_month.days >= 15:
                qtd += 1

        return qtd

    @cached()
    def factor_quantity(self):
        factor = 1.0
        # try:
        #     factor = self.quantity() / float(self.maximum_quantity())
        # except ZeroDivisionError:
        #     factor = 1.0
        # except Exception as e:
        #     log.exception(e)

        return factor

    @cached()
    def event_information(self):
        if self.object:
            return "%s" % (self.object.information if self.object.information else "")

    def base_value(self):
        events = self.base_value_query()
        dt_extra = NewDateRange(self.object.start_validity, self.object.end_validity)
        value = 0
        for e in events:
            days = e.instance_calc().range_calc.intersect(dt_extra).days
            range_days = self.quantity_13() if self._is_christmas_grat else days
            value += e.correct_valor * range_days / e.correct_qnt

        return float(value)


@RunCodeManager.register("gfp-mpto-aid-cumulation-grat")
class AidCumulationGrattification(AidCumulation):

    def configure(self):
        self.validity = NewDateRange(None, date(2016, 12, 31))
        self.validity += NewDateRange(date(2017, 9, 1), None)


@RunCodeManager.register("gfp-mpto-aid-cumulation-13")
class AidCumulationGratificationChristmas(AidCumulation):

    def _get_query_extra(self):
        return ExtraPaymentPeriod.objects.filter(pk__in=self.object.oIds).last()

    def days_quantity(self, obj):
        obj = self._get_query_extra()
        range_salary = self.range_salary_for().intersect(
            NewDateRange(obj.start_validity, obj.end_validity)
        )
        return range_salary.days

    def _query_extra_payments(self):
        q1 = Q(folha__periodo__mes=12) & Q(folha__periodo__ano=self.year)
        query = self.employee.entries.filter(
            Q(evento__in=self.event.relationships) & q1
        )

        return query

    def base_value(self):

        return float(self.object.correct_value)

    def value(self):
        return self.base_value()

    def quantity(self):
        return self.object.qnt

    def event_information(self):
        if self.object:
            return self.object.info

    def unicode_for_obj(self, obj):
        return self.event_information()


@RunCodeManager.register("gfp-mpto-aid-family")
class AidFamily(AidExtraPaymentBaseDependence):
    """
    Premissas para o cálculo:
    -ser dependente economico-financeiro;
    -dependente com idade menor que 6 anos
    """

    title = "Cálculo do Auxílio Familia"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUXILIO-FAMILIA"

    TYPE_AID = 3

    def validate(self):
        self.validate_not_paycheck_pension()


@RunCodeManager.register("gfp-mpto-urv-maternity")
class URVMaternity(URVAdminEmployee):

    def employer_value(self):
        return -self.value()


@RunCodeManager.register("gfp-mpto-abono-permanencia")
class AbonoPermanencia(AidExtraPaymentPercent):

    title = "Abono Permanencia"

    SLUG_EXTRA_PAYMENT_FOR_AID = "ABONO-PERMANENCIA"

    FILTER_EMPLOYEE = True

    PARAMS_ = ["oIds"]

    @cached()
    def factor_quantity(self):
        factor = 1.0
        return factor

    def base_value(self):
        events = self.base_value_query()
        value = 0
        for e in events:
            value += e.correct_valor

        return float(value)

    def quantity(self):
        return 1.0

    def maximum_quantity(self):
        return 1.0


@RunCodeManager.register("gfp-mpto-aid-natality")
class AidNatality(AidExtraPaymentBaseExtraPayment):

    PARAMS_ = ["qnt", "info"]

    title = "Cálculo do Auxílio Natalidade"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUXILIO-NATALIDADE"

    MULTI_CALCULATE = False

    @cached()
    def quantity(self):
        if self.event:
            if "qnt" in self.params and (self.params["qnt"] or self.params["qnt"] == 0):
                return float(self.params["qnt"])
        return 0

    def value(self):
        if self.quantity() > 1:
            return super(AidNatality, self).base_value() * 1.5
        else:
            return super(AidNatality, self).base_value()

    def maximum_quantity(self):
        return 0

    @cached()
    def event_information(self):
        if "info" in self.params and self.params["info"] != "":
            return self.params["info"]
        return super(AidNatality, self).event_information()

    def validate(self):
        pass


@RunCodeManager.register("gfp-mpto-aid-familysalary")
class AidFamilySalary(WorkDaysCalculation):

    title = "Cálculo do Salário Familia"

    SLUG_EXTRA_PAYMENT_FOR_AID = "SALARIO-FAMILIA"

    TYPE_AID = 3

    MULTI_CALCULATE = True

    def _get_query(self):
        query = Dependencia.objects.filter(
            models.Q(
                tipo=self.TYPE_AID,  # IMPOSTO DE RENDA
                suspenso=False,
                data_inicio__lte=self.payroll.date_range.last,
                dependente__servidor=self.employee,
                dependente__grau_parentesco__in=(3, 4, 5, 6, 7, 9),
            )
            & (
                models.Q(data_fim=None)
                | models.Q(data_fim__gte=self.payroll.date_range.first)
            )
        )

        if "oIds" in self.params and self.params["oIds"]:
            query = query.filter(pk__in=self.params["oIds"])

        return query

    def validate(self):
        self.validate_not_paycheck_pension()
        if not self.get_query():
            txt = (
                "O servidor %s não possui depedentes para o salário familia para a folha %s"
                % (self.employee, self.payroll)
            )
            raise self.CalculationNotApplicable(txt)

    def base_socialsecurity(self, total=False):
        return 0.00

    @cache_return
    def family_salary(self):
        return (
            FamilySalary.objects.exclude(
                Q(start_date__gt=self.range_salary.last)
                | (Q(end_date__isnull=True, end_date__lt=self.range_salary.first))
            )
            .order_by("-start_date")
            .first()
        )

    def quantity(self):
        if not self.object:
            return 0
        obj = self.object
        range_salary = self.range_salary_for().intersect(
            NewDateRange(obj.data_inicio, obj.data_fim)
        )
        return range_salary.days

    def event_information(self):
        return self.object.dependente.pessoa_fisica.abbreviation

    def base_value(self):
        return self.range().get("value", 0.00)

    @cache_return
    def range(self):
        family_salary = self.family_salary()
        base_value = super(AidFamilySalary, self).base_value()
        obj = {
            "value": 0.0,
        }

        for family_salary_range in family_salary.ranges.all():
            if base_value >= float(
                family_salary_range.inferior_limit
            ) and base_value <= float(family_salary_range.upper_limit):
                obj["value"] = float(family_salary_range.value)
                break

        return obj

    def employer_value(self):
        ssc = self.employee.get_socialsecurity_by_validity(
            range=self.payroll.date_range
        )
        return -self.value() if ssc.regime == 1 else 0


@RunCodeManager.register("gfp-mpto-aid-hearth-base")
class AidHealthBase(AidExtraPaymentBaseExtraPayment):

    title = "Cálculo do Auxílio Saúde Base"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUXILIO-SAUDE"
    FILTER_EMPLOYEE = True
    MULTI_CALCULATE = False
    ALL_PAYROLL = True
    FILTER_QUERY = 2
    FILTER_BY = 1
    WITHOUT_DAYS = True

    @property
    def references(self):
        return (self.range_salary.first.year, self.range_salary.first.month)

    @property
    def range_query_extra(self):
        return self.range_salary

    def _get_query(self):
        query = self._query_extra_payments()
        # log.debug(self.params)
        return query

    def unicode_for_obj(self, obj):
        text = "%04d%02d" % (
            self.range_salary.first.year,
            self.range_salary.first.month,
        )
        return text


@RunCodeManager.register("gfp-mpto-aid-hearth")
class AidHealth(AidHealthBase):

    title = "Cálculo do Auxílio Saúde"

    def __init__(self, employee, payroll, event=None, **kwargs):
        super(AidHealth, self).__init__(employee, payroll, event, **kwargs)
        self.last_range = self.range_salary.first - relativedelta(days=1)
        self.year = self.last_range.year
        self.month = self.last_range.month
        self.range_salary = NewDateRange.from_month(
            self.year, (self.month if self.month < 12 else 12)
        )
        self.validity = self.range_salary
