# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Q


from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.gfp.classcodes.base import WorkDaysCalculation
from rh.gfp.models import ExtraPaymentPeriod, FolhaEvento
from rh.models import Comarca, Dependencia
from standard.models import RunCodeManager

log = getLogger(__name__)


class BaseExtraPayment(WorkDaysCalculation):

    MULTI_CALCULATE = True

    SLUG_EXTRA_PAYMENT_FOR_AID = ""

    FILTER_EMPLOYEE = False

    FULL_VALUE = True

    def validate(self):
        self.validate_not_paycheck_pension()
        if not self.get_query():
            txt = "O servidor %s não possui pagamento configurado para %s" % (
                self.employee,
                self.SLUG_EXTRA_PAYMENT_FOR_AID,
            )
            raise self.CalculationNotApplicable(txt)

    def _query_extra_payments(self):
        q = ExtraPaymentPeriod.objects.filter(
            extra_payment__slug=self.SLUG_EXTRA_PAYMENT_FOR_AID
        ).filter(
            models.Q(start_validity__lte=self.range_salary.last)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.range_salary.first)
            )
        )
        if self.FILTER_EMPLOYEE:
            q = q.filter(employee=self.employee)

        return q

    def base_value(self):

        if self.object and self.object.type_value == 2:
            value = super(BaseExtraPayment, self).base_value()
        else:
            q = self._query_extra_payments()
            value = float(q[0].value) if q.exists() else 0.00

        return round(value, 2)

    def _filter_repeated_cid(self):
        return self._get_query()

    def _get_query(self):
        query = self._query_extra_payments()
        # log.debug(self.params)

        if "oIds" in self.params and self.params["oIds"]:
            log.debug(self.params)
            query = query.filter(pk__in=self.params["oIds"])

        return query

    def quantity(self):
        if self.object:
            return self.days_quantity(self.object)
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
            "%s - R$ %s"
            % (
                obj.start_validity.strftime("%d-%m-%Y"),
                (("%s%%" if obj.type_value == 2 else "R$ %s") % obj.value),
            )
            if obj
            else ""
        )

    def base_socialsecurity(self):
        return 0


class AidExtraPaymentBaseDependence(WorkDaysCalculation):

    MULTI_CALCULATE = True

    SLUG_EXTRA_PAYMENT_FOR_AID = ""

    TYPE_AID = 0

    def days(self):
        return self.base_days - (self.range_salary.days - self.range_salary_for().days)

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
            models.Q(start_validity__lte=self.range_salary.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.range_salary.first)
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
                data_inicio__lte=self.range_salary.last,
                dependente__servidor=self.employee,
                dependente__grau_parentesco__in=(3, 4, 5, 6, 7, 9),
            )
            & (
                models.Q(data_fim=None)
                | models.Q(data_fim__gte=self.range_salary.first)
            )
        )

        if "oIds" in self.params and self.params["oIds"]:
            query = query.filter(pk__in=self.params["oIds"])

        return query

    def event_information(self):
        return self.object.dependente.pessoa_fisica.abbreviation

    def unicode_for_obj(self, obj):
        return obj.dependente.pessoa_fisica.abbreviation if obj else ""

    def base_socialsecurity(self):
        return 0


class AidExtraPaymentPercent(BaseExtraPayment):

    title = "Cálculo de Verbas adicionais por Percentual"

    MULTI_CALCULATE = True

    @cache_return
    def percentage(self):
        if self.object and self.object.type_value == 2:
            return round(float(self.object.value), 2)
        else:
            return 100.0


@RunCodeManager.register("gfp-aid-supply")
class AidSupply(WorkDaysCalculation):

    title = "Cálculo do Auxílio Alimentação"

    def maximum_quantity(self):
        return 22.0

    @cache_return
    def quantity(self):
        work_days_of_month = self.range_salary.work_days
        print(work_days_of_month)
        worked_days_of_month = self.range_salary_for().work_days
        print(worked_days_of_month)
        qtd_max = self.maximum_quantity()

        if worked_days_of_month == 0:
            return worked_days_of_month

        if work_days_of_month == worked_days_of_month:
            days = qtd_max
        else:
            days = worked_days_of_month

        return days if days < qtd_max else qtd_max

    def _exclude_ranges_for_range_salary(self):
        range_ = super(AidSupply, self)._exclude_ranges_for_range_salary()
        q = (
            self.employee.departures(self.range_salary.first, self.range_salary.last)
            .filter(
                Q(tipo__in=[11, 14, 15, 16, 18, 21, 22, 23, 29, 44, 62])
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

        for l in q.exclude(tipo=11):
            range_ += NewDateRange(l.data_inicio, l.data_fim)

        for l in q.filter(tipo=11):  # Licença Doença Pessoa na Familia > 3 meses
            dt_start = l.data_inicio + relativedelta(months=3)
            if dt_start <= l.data_fim:
                range_ += NewDateRange(dt_start, l.data_fim)

        log.debug("RANGE LICENSES: %s" % range_)

        return range_

    def base_value(self):
        q = ExtraPaymentPeriod.objects.filter(
            extra_payment__slug="AUXILIO-ALIMENTACAO"
        ).filter(
            models.Q(start_validity__lte=self.range_salary.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.range_salary.first)
            )
        )
        return round(float(q[0].value), 2) if q.exists() else 0.00

    def base_socialsecurity(self):
        return 0


@RunCodeManager.register("gfp-aid-supply-ii")
class AidSupplyII(AidSupply):

    def _exclude_ranges_for_range_salary(self):
        range_ = super(AidSupply, self)._exclude_ranges_for_range_salary()
        q = (
            self.employee.departures(self.range_salary.first, self.range_salary.last)
            .filter(
                Q(tipo__in=[11, 14, 15, 16, 18, 21, 22, 23, 29, 44, 62])
                & Q(remunerado=False)
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

        for l in q.exclude(tipo=11):
            range_ += NewDateRange(l.data_inicio, l.data_fim)

        for l in q.filter(tipo=11):  # Licença Doença Pessoa na Familia > 3 meses
            dt_start = l.data_inicio + relativedelta(months=3)
            if dt_start <= l.data_fim:
                range_ += NewDateRange(dt_start, l.data_fim)

        log.debug("RANGE LICENSES: %s" % range_)

        return range_


@RunCodeManager.register("gfp-aid-supply-iii")
class AidSupplyIII(AidSupplyII):

    class AidRange(object):

        def __str__(self):
            return self.pk[4:6] + "/" + self.pk[:4]

    MULTI_CALCULATE = True

    def __init__(self, employee, payroll, event, entry=None, cid=None, **kwargs):
        super(AidSupplyIII, self).__init__(
            employee, payroll, event, entry, cid, **kwargs
        )
        # params = kwargs['params'] if 'params' in kwargs else None

        if self.cid:
            self.year = self.payroll.periodo.ano
            self.month = (
                self.payroll.periodo.mes
                if self.cid == 1
                else (self.payroll.periodo.mes + 1)
            )
            self.range_salary = NewDateRange.from_month(
                self.year, (self.month if self.month < 12 else 12)
            )
            self.validity = self.range_salary

    def get_query(self):

        # 1 - Mês da folha atual
        # 2 - Mês da folha subsequente

        aid_list = []
        log.debug("%s/%s" % (self.month, self.year))
        log.debug(self.range_salary)
        q_paid = FolhaEvento.objects.filter(
            contracheque__servidor=self.employee,
            evento=self.event,
            reference_month=self.payroll.periodo.mes,
            reference_year=self.payroll.periodo.ano,
            contracheque__pensioner=None,
        )
        log.debug("pagos")
        log.debug(q_paid.exists())
        if self.entry:
            q_paid = q_paid.exclude(pk=self.entry.pk)

        # log.debug('GET_QUERY: %s %s' % (self.__class__.__name__, q_paid.count()))
        if not q_paid.exists():
            log.debug("nao existe")
            aid_list.append(1)

        if self.payroll.periodo.mes < 12:
            aid_list.append(2)
        log.debug(self._cid)
        log.debug(1 in aid_list)
        if self._cid and int(self._cid) in aid_list:
            log.debug("entrou")
            aid_list = [self._cid]
        log.debug(aid_list)
        return aid_list

    def validate(self):
        # for q in self.get_query():
        log.debug(type(self.object))
        if self.object:
            log.debug("a entry %s" % self.entry)
            month_temp = (
                self.payroll.periodo.mes
                if int(self.object) == 1
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

            log.debug(self.entry)
            if self.entry:
                log.debug("aquio")
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
        log.debug(self.object)
        # if self.object:
        return super(AidSupplyIII, self).base_value()
        # return 0.0

    def unicode_for_obj(self, obj):
        text = "%04d%02d" % (self.year, self.month)
        return text


@RunCodeManager.register("gfp-aid-daycare")
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


@RunCodeManager.register("gfp-aid-special")
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


@RunCodeManager.register("gfp-aid-habitation")
class AidHabitation(WorkDaysCalculation):
    """
    Premissas para o cálculo:
    - Ser membro do mp
    """

    title = "Cálculo do Auxílio Moradia"

    MULTI_CALCULATE = True

    @cache_return
    def get_possessions(self):
        possessions = (
            self.employee.posses.exclude(
                models.Q(data_exercicio__gt=self.range_salary.last)
            )
            .filter(
                models.Q(desligamento=None)
                | models.Q(desligamento__data_desligamento__gte=self.range_salary.first)
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
            models.Q(start_validity__lte=self.range_salary.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.range_salary.first)
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
                log.debug("AID HABITATION: %s - %s" % (_range, d))
            return date_range.days

        return 0

    def _get_query(self):
        if self.params.get("oIds"):
            return Comarca.objects.filter(pk__in=self.params.get("oIds"))
        else:
            comarcas = set()
            query = self.employee.servidor_lotacao.exclude(
                data_vigencia_fim__lt=self.range_salary.first
            ).filter(data_vigencia_inicio__lte=self.range_salary.last)
            for row in query:
                comarcas.add(row.lotacao.comarca)
            comarcas = list(comarcas)

            return comarcas

    def event_information(self):
        return self.object

    def base_socialsecurity(self):
        return 0


@RunCodeManager.register("gfp-aid-cumulation")
class AidCumulation(AidExtraPaymentPercent):

    PARAMS_ = ["info", "qnt", "pct", "oIds"]

    SLUG_EXTRA_PAYMENT_FOR_AID = "CUMULATION"
    FILTER_EMPLOYEE = True
    FULL_VALUE = False

    def configure(self):
        self.validity = NewDateRange(datetime(2016, 1, 1), datetime(2017, 8, 31))

    @cache_return
    def quantity(self):
        log.debug("RECALCULATE QNT: %s %s" % (self.params, self.entry.correct_qnt))
        if self.event:
            if "qnt" in self.params and (self.params["qnt"] or self.params["qnt"] == 0):
                return float(self.params["qnt"])
            if self.entry:
                return float(self.entry.correct_qnt)
        return super(AidCumulation, self).quantity()

    @cache_return
    def percentage(self):
        if "pct" in self.params and float(self.params["pct"] or 0) != 0.0:
            return float(self.params["pct"] or super(AidCumulation, self).percentage())
        if self.entry:
            return float(self.entry.correct_pct)
        return super(AidCumulation, self).percentage()

    @cache_return
    def event_information(self):
        if "info" in self.params and self.params["info"] != "":
            return self.params["info"]
        return super(AidCumulation, self).event_information()


@RunCodeManager.register("gfp-urv-admin-employee")
class URVAdminEmployee(AidExtraPaymentPercent):

    PARAMS_ = ["oIds"]

    SLUG_EXTRA_PAYMENT_FOR_AID = "URV-ADMIN-EMPLOYEE"
    FILTER_EMPLOYEE = True
    FULL_VALUE = True

    # @cache_return
    # def factor_quantity(self):
    #     return 1.0

    @cache_return
    def event_information(self):
        if self.object:
            return "%s" % (self.object.information if self.object.information else "")

    # def base_value(self):
    #     events = self.base_value_query()
    #     value = 0
    #     for e in events:
    #         value += e.correct_valor

    #     return float(value)

    def base_socialsecurity(self):
        return self.value()


@RunCodeManager.register("gfp-urv-admin-efective")
class URVAdminEfective(URVAdminEmployee):

    def base_socialsecurity(self):
        return self.value()


@RunCodeManager.register("gfp-urv-admin-comissioned")
class URVAdminComissioned(URVAdminEmployee):

    def base_socialsecurity(self):
        ssc = self.employee.get_socialsecurity_by_validity(
            range=self.payroll.date_range
        )
        regime_social_security = ssc.regime if ssc else None
        return 0 if regime_social_security in [2, 3] else self.value()


@RunCodeManager.register("gfp-aid-cumulation-grat")
class AidCumulationGrattification(AidCumulation):

    CALCULATE_OVER = 3
    FULL_VALUE = True

    def __init__(self, employee, payroll, event=None, **kwargs):
        """
        Inicializador do calculo, recebe o servidor, folha a ser calculada e o evento que possui o calculo automático.
        """
        log.debug(">>> %s <<<" % self.__class__)
        super(AidCumulationGrattification, self).__init__(
            employee, payroll, event, **kwargs
        )
        self.full_value = True

    def configure(self):
        self.validity = NewDateRange(None, datetime(2016, 12, 31))
        self.validity += NewDateRange(datetime(2017, 9, 1), None)

    # def base_socialsecurity(self):
    #     return self.value()


@RunCodeManager.register("gfp-aid-family")
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


@RunCodeManager.register("gfp-urv-maternity")
class URVMaternity(URVAdminEmployee):

    def employer_value(self):
        return -self.value()
