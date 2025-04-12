# -*- coding: utf-8 -*-

from datetime import date, datetime
from calendar import monthrange

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Q
from memoization import cached

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.const import CANCELADO as AFASTAMENTO_CANCELADO
from rh.gfp.calcs.mpmt.base import WorkDaysCalculation
from rh.gfp.calcs.mpmt.remuneracao import SalaryEffective
from rh.gfp.models import EstruturaTabelaSalarial, ExtraPaymentPeriod, Periodo, Evento
from rh.models import (
    Cargo,
    Comarca,
    Dependencia,
    MembersTelecommuting,
    Quadro,
    MovimentacaoDiligencia,
    Lotacao,
    WorkplaceConfigTag,
)
from standard.models import RunCodeManager
from rh.models import ServidorLotacao

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
        self.validate_if_employee_not_in_slug_extra()

    def _query_extra_payments(self):
        slugs = (
            self.SLUG_EXTRA_PAYMENT_FOR_AID
            if isinstance(self.SLUG_EXTRA_PAYMENT_FOR_AID, tuple)
            else (self.SLUG_EXTRA_PAYMENT_FOR_AID,)
        )
        q = ExtraPaymentPeriod.objects.filter(extra_payment__slug__in=slugs).filter(
            models.Q(start_validity__lte=self.payroll.date_range.last)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        if self.FILTER_EMPLOYEE:
            q = q.filter(employee=self.employee)

        if self.FILTER_BY_TYPE:
            q = q.filter(type_value=self.FILTER_BY_TYPE)

        return q

    def base_value(self):
        log.info(
            f"_value_calc_normatized ****************** {self.object and self.object.type_value}"
        )

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
            return self.object.information
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

    def _query_extra_payments_for_qtd(self):
        if isinstance(self.SLUG_EXTRA_PAYMENT_FOR_AID, tuple):
            slugs = self.SLUG_EXTRA_PAYMENT_FOR_AID
        else:
            slugs = (self.SLUG_EXTRA_PAYMENT_FOR_AID,)
        return ExtraPaymentPeriod.objects.filter(
            employee=self.employee,
            extra_payment__slug__in=slugs,
        ).filter(
            Q(start_validity__year=self.year)
            | Q(end_validity__year__gte=self.year)
            | Q(end_validity__isnull=True)
        )

    def quantity_13_extra_pay(self):
        q_extra_pay = self._query_extra_payments_for_qtd()
        qtd = 0
        if q_extra_pay.count() == 1:
            extra_pay = q_extra_pay.first()
            if (
                extra_pay.start_validity.year < self.year
                and extra_pay.end_validity is None
            ):
                qtd = self.maximum_quantity()
            else:
                for month in range(1, 13):
                    range_month = NewDateRange.range_from_month(self.year, month)
                    if extra_pay.start_validity < range_month[0] or (
                        extra_pay.start_validity.month == month
                        and extra_pay.start_validity.day < (range_month[1].day / 2)
                    ):
                        qtd += 1
        else:
            for extra_pay in q_extra_pay:
                extra_range = NewDateRange(
                    extra_pay.start_validity, extra_pay.end_validity
                )
                range_month = self.range_13salary.intersect(extra_range)
                qtd += (range_month.last.month - range_month.first.month) + 1

        return qtd


class AidExtraWithoutDays(AidExtraPaymentBaseExtraPayment):

    def days_quantity(self, obj):
        range_salary = self.range_salary.intersect(
            NewDateRange(obj.start_validity, obj.end_validity)
        )
        qtd_max = self.maximum_quantity()
        return range_salary.days if range_salary.days < qtd_max else qtd_max


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
        slugs = (
            self.SLUG_EXTRA_PAYMENT_FOR_AID
            if isinstance(self.SLUG_EXTRA_PAYMENT_FOR_AID, tuple)
            else (self.SLUG_EXTRA_PAYMENT_FOR_AID,)
        )
        q = ExtraPaymentPeriod.objects.filter(extra_payment__slug__in=slugs).filter(
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
                tipo=self.TYPE_AID,
                suspenso=False,
                data_inicio__lte=self.payroll.date_range.last,
                dependente__servidor=self.employee,
                dependente__grau_parentesco__in=(3, 4, 5, 6, 7, 9),
            )
            & (
                models.Q(data_fim=None)
                | models.Q(data_fim__gte=self.payroll.date_range.first)
            )
        ).order_by("-data_fim")

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


@RunCodeManager.register("gfp-mpmt-aid-supply")
class AidSupply(WorkDaysCalculation):

    title = "Cálculo do Auxílio Alimentação"

    def get_possession_office(self):
        # 00119 - CARGO AUXILIAR MINISTERIAL-MPMT
        cargo_codigo = "00119"

        return Cargo.objects.get(codigo=cargo_codigo)

    def validate_if_active_possession_office(self):
        job_position = self.employee.job_position(self.payroll.date_range.last)
        if job_position is None:
            txt = f"O Servidor não tem Movimentação Posse ou Declaração de Atividade ativa neste período."
            raise self.CalculationNotApplicable(txt)

    def validate_not_in_possession_office(self):
        possessions = self.get_possessions()
        cargo = self.get_possession_office()
        cargo_possessions = possessions.filter(quadro__cargo=cargo)
        if possessions.count() == cargo_possessions.count():
            txt = f"Servidores com o cargo de {cargo.nome} não tem direito à Aux. Alimentação"
            raise self.CalculationNotApplicable(txt)

    def validate_type_by_possession(self):
        if self.employee.type_by_possession in ("SAP", "MAP", "MAP2", "BFP", "APO"):
            txt = f"O servidor {self.employee} não tem direito à Aux. Alimentação."
            raise self.CalculationNotApplicable(txt)

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validate_if_active_possession_office()
        # self.validate_not_in_possession_office()
        self.validate_type_by_possession()

    def maximum_quantity(self):
        return 30.0

    def employee_in_slug_exception(self):
        q = ExtraPaymentPeriod.objects.filter(
            employee=self.employee, extra_payment__slug="AUXILIO-ALIMENTACAO"
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.last)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )

        return q.first() if q.exists() else None

    @cached()
    def quantity(self):
        days = 0
        qtd_max = self.maximum_quantity()
        for possession in self.get_possessions():
            range_salary = self.range_salary_for(possession=possession)
            days += range_salary.business_days

        slug_exception = self.employee_in_slug_exception()
        if slug_exception:
            dt = NewDateRange()
            month_last_day = dt.range_from_month(
                self.payroll.periodo.ano, self.payroll.periodo.mes
            )[-1]

            if slug_exception.end_validity > month_last_day:
                end_range = month_last_day
            else:
                end_range = slug_exception.end_validity

            dt_range = NewDateRange(slug_exception.start_validity, end_range)
            total_dias = days - dt_range.days
            days = 0 if total_dias < 0 else total_dias

        return days if days < qtd_max else qtd_max

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        range_ = super(AidSupply, self)._exclude_ranges_for_range_salary(
            range_salary=range_salary
        )
        tipos = [18, 44]
        map_suspend_after = {}
        create_map_suspend = False

        q = self.employee.departures(
            self.payroll.periodo.range.first, self.payroll.periodo.range.last
        )

        if self.employee.type_by_possession in ["MBR", "MEL", "MCM", "MEC"]:
            create_map_suspend = True
            tipos = [18, 44, 62]

            q = q.filter(tipo__in=tipos)
        elif self.employee.type_by_possession in ["CMS", "EFE", "ECM", "EFC"]:
            create_map_suspend = True
            tipos = [9, 10, 11, 14, 16, 17, 18, 37, 44, 59]

            q = (
                q.filter(Q(tipo__in=tipos))
                .filter(
                    ~Q(afastamento__afastamentooutroorgao__transito_pela_folha=True)
                )
                .exclude(Q(servidor__tipo="M"))
            )

        if create_map_suspend:
            map_suspend_after = {
                9: 15,  # Licença saúde suspender após 15 dias
                10: 15,  # Licença saúde suspender após 15 dias
                11: 5,  # Licença saúde pessoa da familia suspender após 5 dias
                37: 15,  # Licença saúde suspender após 15 dias
            }

        if map_suspend_after:
            for l in q.filter():
                days_suspend_after = map_suspend_after.get(l.tipo, 0)
                dt_start = l.data_inicio + relativedelta(days=days_suspend_after)
                dt_end = (
                    self.payroll.periodo.range.last
                    if l.data_fim is None
                    else l.data_fim
                )
                if dt_start <= dt_end:
                    range_ += NewDateRange(dt_start, l.data_fim)
                    log.info(f"dias: {range_}")
                elif not days_suspend_after == 0:
                    range_ = NewDateRange(0, 0)

        return range_

    def base_value(self):
        q = ExtraPaymentPeriod.objects.filter(
            employee=None, extra_payment__slug="AUXILIO-ALIMENTACAO"
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )
        return round(float(q[0].value), 2) if q.exists() else 0.00


@RunCodeManager.register("gfp-mpmt-aid-daycare")
class AidDaycare(AidExtraPaymentBaseDependence):
    """
    Premissas para o cálculo:
    -ser dependente economico-financeiro;
    -dependente com idade menor que 6 anos
    """

    title = "Cálculo do Auxílio Creche"

    MULTI_CALCULATE = False

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUXILIO-CRECHE"

    TYPE_AID = 4

    FILTER_CID = 0

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validar_tipo_posse()

    def validar_tipo_posse(self):
        if self.employee.tipo == "M":
            raise self.CalculationNotApplicable("Membro não tem direito a Aux. Creche!")

    def quantity(self):
        return len(self.get_query())

    def maximum_quantity(self):
        return 1

    def _get_query(self):
        data_folha = datetime(self.year, self.month, 1).date()
        query = (
            super()._get_query().order_by("data_fim").exclude(data_fim__lte=data_folha)
        )

        if query.count() > 2:
            return query[:2]

        return query

    def _value_for_dep(self, dep, valor):
        range_dep = self.range_base.intersect(
            NewDateRange(dep.data_inicio, dep.data_fim)
        )
        return (valor / self.range_salary.days) * range_dep.days

    @cached()
    def value(self):
        valor = 0
        valor_base = self.base_value()
        valor_max = self.ceiling
        query_list = self.get_query()

        if len(query_list) == 0:
            valor = 0
        elif len(query_list) == 1:
            valor = self._value_for_dep(query_list[0], valor_base)
        else:
            valor_dep_1 = self._value_for_dep(query_list[0], valor_base)
            valor_dep_2 = self._value_for_dep(query_list[1], valor_max - valor_base)
            valor = valor_dep_1 + valor_dep_2

        if valor > valor_max:
            valor = valor_max

        return valor

    def event_information(self):
        return ""

    @property
    def oIds(self):
        return []


@RunCodeManager.register("gfp-mpmt-aid-retroactivedaycare")
class AidRetroactiveDaycare(AidDaycare):
    """
    Premissas para o cálculo:
    -ser dependente economico-financeiro;
    -dependente com idade menor que 6 anos
    -data início do auxílio menor que a data atual
    """

    title = "Cálculo do Auxílio Creche - Meses Anteriores"

    def __init__(self, employee, payroll, event=None, **kwargs):
        super(AidRetroactiveDaycare, self).__init__(employee, payroll, event, **kwargs)

        dep = self.get_dependencia()
        if dep:
            data_retroativo = self.ultimo_dia_mes_anterior(dep)
            self.range_salary = NewDateRange(dep.data_inicio, data_retroativo)

    def validate(self):
        self.validate_not_paycheck_pension()
        self.validar_tipo_posse()

    def validar_tipo_posse(self):
        if self.employee.tipo == "M":
            raise self.CalculationNotApplicable("Membro não tem direito a Aux. Creche!")

    def get_dependencia(self):
        query_list = self.get_query()
        if len(query_list) > 0:
            dep = query_list[0]
            return dep
        raise self.CalculationNotApplicable(
            "Não foram encontradas Dependências do tipo Aux. Creche!"
        )

    def ultimo_dia_mes_anterior(self, dep):
        data_retroativo = dep.created_at.date() - relativedelta(
            months=1
        )  # subtrai o mês
        return data_retroativo.replace(
            day=monthrange(data_retroativo.year, data_retroativo.month)[1]
        )  # último dia do mês

    def quantity(self):
        dep = self.get_dependencia()
        return self.qtd_por_dependencia(dep)

    def qtd_por_dependencia(self, dep):
        if dep:
            data_retroativo = self.ultimo_dia_mes_anterior(dep)
            range_dep = self.range_base.intersect(
                NewDateRange(dep.data_inicio, data_retroativo)
            )
            return range_dep.days
        return 0

    def maximum_quantity(self):
        hoje = datetime.now()
        q_config = self.event.configs.filter(
            start_validity__lte=hoje,
        ).filter(Q(end_validity__isnull=True) | Q(end_validity__gte=hoje))
        if q_config.exists():
            return float(q_config.first().max_quantity)
        return 1

    def buscar_config_vigente(self):
        hoje = datetime.now()
        q_config = self.event.configs.filter(
            start_validity__lte=hoje,
        ).filter(Q(end_validity__isnull=True) | Q(end_validity__gte=hoje))

        return (
            q_config.order_by("-start_validity").first() if q_config.exists() else None
        )

    def base_value(self):
        config_vigente = self.buscar_config_vigente()

        return float(config_vigente.base_value)

    def get_qtd_dependentes(self):
        return Dependencia.objects.filter(
            tipo=self.TYPE_AID, dependente__servidor=self.employee, suspenso=False
        ).count()

    def get_dependentes(self):
        return Dependencia.objects.filter(
            tipo=self.TYPE_AID, dependente__servidor=self.employee, suspenso=False
        )

    def _get_query(self):
        hoje = datetime.now()
        query = Dependencia.objects.filter(
            models.Q(
                tipo=self.TYPE_AID,
                created_at__month=hoje.month,
                created_at__year=hoje.year,
                dependente__servidor=self.employee,
                suspenso=False,
            )
            & (
                models.Q(data_inicio__year=hoje.year, data_inicio__month__lt=hoje.month)
                | models.Q(data_inicio__year__lt=hoje.year)
            )
        ).order_by("data_inicio")

        if query.count() > 2:
            return query[:2]

        return query

    def _value_for_dep(self, valor, qtd):
        return (valor / self.maximum_quantity()) * qtd

    def _value_for_dep1(self, dep):
        valor_base, valor_max = self.get_valor_base_max()
        return self._value_for_dep(valor_base, self.qtd_por_dependencia(dep))

    def _value_for_dep2(self, dep):
        valor_base, valor_max = self.get_valor_base_max()
        return self._value_for_dep(
            valor_max - valor_base, self.qtd_por_dependencia(dep)
        )

    def get_valor_base_max(self):
        config_vigente = self.buscar_config_vigente()
        valor_base = self.base_value()
        valor_max = float(config_vigente.ceiling)
        return valor_base, valor_max

    @cached()
    def value(self):
        valor = 0
        valor_base, valor_max = self.get_valor_base_max()

        if self.get_qtd_dependentes() > 1:
            count = 1
            for dep in self.get_dependentes():
                if count == 1:
                    if dep in self.get_query():
                        valor_dep_1 = self._value_for_dep1(dep)
                    else:
                        valor_dep_1 = 0
                else:
                    if dep in self.get_query():
                        valor_dep_2 = self._value_for_dep2(dep)
                    else:
                        valor_dep_2 = 0
                count += 1
            valor = valor_dep_1 + valor_dep_2
        else:
            valor = self._value_for_dep(
                valor_base, self.qtd_por_dependencia(self.get_dependentes().first())
            )

        return valor


@RunCodeManager.register("gfp-mpmt-aid-special")
class AidSpecial(AidExtraPaymentBaseDependence):
    """
    Premissas para o cálculo:
    -ser dependente economico-financeiro;
    -possuir alguma deficiencia
    """

    title = "Cálculo do Auxílio Especial"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUXILIO-ESPECIAL"

    TYPE_AID = 6

    FILTER_CID = 2


@RunCodeManager.register("gfp-mpmt-aid-habitation")
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


@RunCodeManager.register("gfp-mpmt-aid-cumulation")
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


@RunCodeManager.register("gfp-mpmt-urv-admin-employee")
class URVAdminEmployee(AidExtraPaymentPercent):

    PARAMS_ = ["oIds"]

    SLUG_EXTRA_PAYMENT_FOR_AID = "URV-ADMIN-EMPLOYEE"
    FILTER_EMPLOYEE = True
    FULL_VALUE = True

    @cached()
    def quantity_13(self):
        # vai pro base salary; avaliar self._is_christmas_grat
        range_period = self.range_13salary
        log.debug(range_period)
        log.debug(self._exclude_ranges_for_range_salary())
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


@RunCodeManager.register("gfp-mpmt-aid-cumulation-grat")
class AidCumulationGrattification(AidCumulation):

    def configure(self):
        self.validity = NewDateRange(None, date(2016, 12, 31))
        self.validity += NewDateRange(date(2017, 9, 1), None)


@RunCodeManager.register("gfp-mpmt-aid-cumulation-13")
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


@RunCodeManager.register("gfp-mpmt-aid-family")
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


@RunCodeManager.register("gfp-mpmt-urv-maternity")
class URVMaternity(URVAdminEmployee):

    def employer_value(self):
        return -self.value()


@RunCodeManager.register("gfp-mpmt-abono-permanencia")
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


@RunCodeManager.register("gfp-mpmt-dif-submp-fc-i")
class SubDifferenceMPFCI(AidExtraPaymentPercent):

    title = "Diferença Sub MP-FC-I"

    SLUG_EXTRA_PAYMENT_FOR_AID = "DIF-SUBMP-FC"

    FILTER_EMPLOYEE = True

    @cached()
    def factor_quantity(self):
        factor = 1.0
        return factor

    def quantity(self):
        return 1.0

    def maximum_quantity(self):
        return 1.0


@RunCodeManager.register("gfp-mpmt-aid-natality")
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


@RunCodeManager.register("gfp-mpmt-aid-earnings-s")
class AidExtraEarningsS(AidExtraPaymentBaseExtraPayment):

    title = "Cálculo de provento para servidor aposentado"

    SLUG_EXTRA_PAYMENT_FOR_AID = ("PROVENTO_SERVIDOR", "PROVENTO_MEMBRO")

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-earnings-m")
class AidExtraEarningsM(AidExtraWithoutDays):

    title = "Cálculo de provento para membro aposentado"

    SLUG_EXTRA_PAYMENT_FOR_AID = "PROVENTO_MEMBRO"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-benefit")
class AidExtraBenefit(AidExtraWithoutDays):

    title = "Cálculo de benefício para pensionista"

    SLUG_EXTRA_PAYMENT_FOR_AID = "BENEFICIO"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-end-career")
class AidExtraEndCareer(AidExtraWithoutDays):

    title = "Adicional Fim de Carreira"

    SLUG_EXTRA_PAYMENT_FOR_AID = "ADD-FIM-CARREIRA"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-end-career-inc-ir")
class AidExtraEndCareerIncIr(AidExtraWithoutDays):

    title = "Adicional Fim de Carreira - INC. IR"

    SLUG_EXTRA_PAYMENT_FOR_AID = "ADD-FIM-CARREIRA-INC-IR"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-art37xv")
class AidExtraEarningsArt37XV(AidExtraWithoutDays):

    title = "Cálculo de Vantagem Constitucional Art. 37 XV"

    SLUG_EXTRA_PAYMENT_FOR_AID = "VANTAGEM_ART37XV"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-art37xv-inc-ir")
class AidExtraEarningsArt37XVIncIr(AidExtraWithoutDays):

    title = "Cálculo de Vantagem Constitucional Art. 37 XV - INC. IR"

    SLUG_EXTRA_PAYMENT_FOR_AID = "VANTAGEM_ART37XV-INC-IR"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-incorporated-vantage")
class AidExtraEarningsIncorporated(AidExtraWithoutDays):

    title = "Cálculo de Vantagem Incorporada"

    SLUG_EXTRA_PAYMENT_FOR_AID = "VALOR-INCORPORADO"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-gaeco-servidores")
class AidExtraGaecoServidores(AidExtraPaymentPercent):

    title = "Cálculo de GAECO SERVIDORES"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GAECO-SERVIDORES"

    FILTER_EMPLOYEE = True

    def quantity(self):
        return self.maximum_quantity()


@RunCodeManager.register("gfp-mpmt-aid-prevcom")
class AidExtraPrevcom(AidExtraWithoutDays):

    title = "Cálculo de PREVCOM "

    SLUG_EXTRA_PAYMENT_FOR_AID = "SPPREVCOM"

    FILTER_EMPLOYEE = True

    PARAMS_ = ["info", "oIds", "qnt", "pct"]

    def quantity(self):
        return self.maximum_quantity()


@RunCodeManager.register("gfp-mpmt-aid-prevcom-i-invalidez")
class AidExtraPrevcomIInvalidez(AidExtraWithoutDays):

    title = "Cálculo de PREVCOM I - Invalidez"

    SLUG_EXTRA_PAYMENT_FOR_AID = "SP-PREVCOM-I-INVALIDEZ"

    FILTER_EMPLOYEE = True

    def quantity(self):
        return self.maximum_quantity()


@RunCodeManager.register("gfp-mpmt-aid-prevcom-ii-morte")
class AidExtraPrevcomIIMorte(AidExtraWithoutDays):

    title = "Cálculo de PREVCOM II - Pensão por Morte"

    SLUG_EXTRA_PAYMENT_FOR_AID = "SP-PREVCOM-II-MORTE"

    FILTER_EMPLOYEE = True

    def quantity(self):
        return self.maximum_quantity()


@RunCodeManager.register("gfp-mpmt-aid-grat-collection")
class AidExtraGratificationCollection(AidExtraPaymentBaseExtraPayment):

    title = "Gratificação de Acervo"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-ACERVO"

    FILTER_EMPLOYEE = True

    def base_value(self):
        possession = self.get_possessions_by_type(["EF"]).first()
        base_value = 0.0
        if possession:
            range_ = self.range_salary_for(possession)
            salaries = EstruturaTabelaSalarial.salarios(
                possession.quadro.cargo, range_.first, range_.last
            )
            salarie = salaries[0][1]
            initial_salary = salarie.tabela_salarial.salarios.order_by(
                "referencia_nivel2d__ordem"
            ).first()
            base_value = initial_salary.valor_membro

        return float(base_value)


class AidExtraBase(AidExtraPaymentBaseExtraPayment):
    """Classe base a ser herdada para classes de configurações de verbas"""

    # EMPLOYEE_TIPO default: tipo de Employee como Membro
    EMPLOYEE_TIPO = "M"

    # POSSESSION_TYPE default: 'EF' (Efetivo)
    POSSESSION_TYPE = ["EF"]

    # POSSESSION_TYPE default: cargo de Promotor de Justiça Substituto - MPMT
    CARGO_CODIGO = "00085"

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.employee.tipo != self.EMPLOYEE_TIPO:
            raise self.CalculationNotApplicable("Não tem direito!")

    def get_fixed_office(self):
        return Cargo.objects.get(codigo=self.CARGO_CODIGO)

    def get_last_possession_office(self):
        return self.employee.posses_ativas.last().quadro.cargo

    def get_salaries(self, cargo_recebe):
        range_ = self.payroll.date_range

        salaries = EstruturaTabelaSalarial.salarios(
            cargo_recebe, range_.first, range_.last
        )

        return salaries[0][1]

    def return_to_base_value(self, salarie):
        if self.EMPLOYEE_TIPO == "M":
            return salarie.valor_membro
        else:
            return salarie.valor

    def get_salarie_from_initial_salary(self, cargo_recebe):
        salarie = self.get_salaries(cargo_recebe)

        initial_salary = salarie.tabela_salarial.salarios.order_by(
            "referencia_nivel2d__ordem"
        ).first()

        return self.return_to_base_value(initial_salary)

    def get_salarie_from_salaries(self, cargo_recebe):
        salarie = self.get_salaries(cargo_recebe)

        return self.return_to_base_value(salarie)


class AidExtraFixedOfficeBase(AidExtraBase):

    def base_value(self):
        possession = self.get_possessions_by_type(self.POSSESSION_TYPE).first()
        base_value = 0.0

        if possession:
            cargo_recebe = self.get_fixed_office()
            base_value = self.get_salarie_from_initial_salary(cargo_recebe)

        return float(base_value)


class AidExtraLastPossessionOfficeBase(AidExtraBase):

    def base_value(self):
        possession = self.get_possessions_by_type(self.POSSESSION_TYPE).first()
        base_value = 0.0

        if possession:
            cargo_recebe = self.get_last_possession_office()
            base_value = self.get_salarie_from_salaries(cargo_recebe)

        return float(base_value)


@RunCodeManager.register("gfp-mpmt-aid-desig-cumul-exec-func-subst-mem")
class AidExtraDesigCumulExecFuncSubstMem(AidExtraFixedOfficeBase):

    title = "Designação Exercício Cumulativo de Funções - Membros Substitutos"

    SLUG_EXTRA_PAYMENT_FOR_AID = "DESIG-EXERC-CUMUL-FUNC-MEM-SUBST"


@RunCodeManager.register("gfp-mpmt-aid-cumul-exec-subst-mem")
class AidExtraCumulExecSubstMem(AidExtraFixedOfficeBase):

    title = "Exercício Cumulativo - Membros Substitutos"

    SLUG_EXTRA_PAYMENT_FOR_AID = "EXERC-CUMUL-MEM-SUBST"


@RunCodeManager.register("gfp-mpmt-aid-repr-art82-lc27-93")
class AidExtraRepresentationBonusArt82LC2793(AidExtraLastPossessionOfficeBase):

    title = "Gratificação de Representação - ART. 82 L.C 27/93"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-REPR-ART82-LC27-93"


@RunCodeManager.register("gfp-mpmt-aid-repr-ato-358-2011")
class AidExtraRepresentationBonusAto3582011(AidExtraLastPossessionOfficeBase):

    title = "Gratificação de Representação - ATO 358/2011"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-REPR-ATO-358-2011"


@RunCodeManager.register("gfp-mpmt-aid-repr-art147-lc416-2010")
class AidExtraRepresentationBonusArt147LC4162010(AidExtraLastPossessionOfficeBase):

    title = "Gratificação de Representação - ART. 147 L.C 416/2010"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-REPR-ART147-LC416-2010"


@RunCodeManager.register("gfp-mpmt-aid-grat-fun-org-aux")
class AidExtraAuxOrgFuncBonus(AidExtraLastPossessionOfficeBase):

    title = "Gratificação Função Órgãos Auxiliares"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-FUNC-ORGAOS-AUX"


@RunCodeManager.register("gfp-mpmt-aid-grat-diff-desig-adm-sup")
class AidExtraDiffSuperiorAdminBonus(AidExtraLastPossessionOfficeBase):

    title = "Gratificação Diferença Designação Admin. Superior"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-DIFF-DESIG-ADMIN-SUP"


@RunCodeManager.register("gfp-mpmt-aid-superior-council-bonus")
class AidExtraSuperiorCouncilBonus(AidExtraLastPossessionOfficeBase):

    title = "Gratificação Conselho Superior Membros MP"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-CONS-SUP-MEMBROS"


@RunCodeManager.register("gfp-mpmt-aid-add-bonus")
class AidExtraAdditionalBonus(AidExtraLastPossessionOfficeBase):

    title = "Gratificação Adicional de Membros"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-ADICIONAL-MEMBROS"


@RunCodeManager.register("gfp-mpmt-aid-grat-diff-prov")
class AidExtraGratificationDiffProv(AidExtraFixedOfficeBase):

    title = "Gratificação de Diferença Provimento"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRAT-DIFF-PROV"

    EMPLOYEE_TIPO = "S"

    # cargo de Técnico Administrativo - MPMT
    CARGO_CODIGO = "00099"


@RunCodeManager.register("gfp-mpmt-aid-police")
class AidExtraGratificationPolice(AidExtraWithoutDays):

    title = "Gratificação Policial"

    SLUG_EXTRA_PAYMENT_FOR_AID = "GRATIFICACAO-POLICIAL"

    FILTER_EMPLOYEE = True


@RunCodeManager.register("gfp-mpmt-aid-desig-prom-dif-prov")
class AidExtraDesignacaoPromDifProv(AidExtraFixedOfficeBase):

    title = "Designação Promotoria Difícil Provimento"

    SLUG_EXTRA_PAYMENT_FOR_AID = "DESIG-PROM-DIF-PROV"


@RunCodeManager.register("gfp-mpmt-aid-change-20")
class AidExtraChange20(AidExtraFixedOfficeBase):

    title = "Auxílio Mudança Indenizatória - Membros - 20%"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUX-MUDANCA-20"


@RunCodeManager.register("gfp-mpmt-aid-change-50")
class AidExtraChange50(AidExtraFixedOfficeBase):

    title = "Auxílio Mudança Indenizatória - Membros - 50%"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AUX-MUDANCA-50"


@RunCodeManager.register("gfp-mpmt-aid-cumulative-exercises")
class AidExtraCumulativeExercises(SalaryEffective):

    title = "Exercício Cumulativo"

    # EMPLOYEE_TIPO default: tipo de Employee como Membro
    EMPLOYEE_TIPO = "M"

    # POSSESSION_TYPE default: 'EF' (Efetivo)
    POSSESSION_TYPE = ["EF"]

    # CARGO_CODIGO default: cargo de Promotor de Justiça Substituto - MPMT
    CARGO_CODIGO = "00085"

    PARAMS_ = ["info", "oIds", "qnt"]

    def validate_if_is_member(self):
        if self.employee.tipo != self.EMPLOYEE_TIPO:
            raise self.CalculationNotApplicable(
                "Somente Membros tem direito a essa verba!"
            )

    def validate(self):
        self.validate_if_is_member()

    def get_possessions_by_type(self, types=[]):
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

    def get_salaries(self, cargo_recebe):
        range_ = self.payroll.date_range

        salaries = EstruturaTabelaSalarial.salarios(
            cargo_recebe, range_.first, range_.last
        )

        return salaries[0][1]

    def base_value(self):
        possession = self.get_possessions_by_type(self.POSSESSION_TYPE).first()
        base_value = 0.0

        if possession:
            cargo_recebe = Cargo.objects.get(codigo=self.CARGO_CODIGO)
            salarie = self.get_salaries(cargo_recebe)
            initial_salary = salarie.tabela_salarial.salarios.order_by(
                "referencia_nivel2d__ordem"
            ).first()

            base_value = initial_salary.valor_membro

        return float(base_value)

    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            try:
                return float(self.params["qnt"])
            except Exception:
                return self._base_value[1]
        else:
            return (
                self._base_value[1]
                if not self._is_christmas_grat
                else self.quantity_13()
            )


@RunCodeManager.register("gfp-mpmt-aid-cumulative-exercises-permanent")
class AidExtraCumulativeExercisesPermanent(AidExtraCumulativeExercises):

    title = "Exercício Cumulativo Permanente"

    def validate_if_workplace_has_cumulative_tag(self):
        workplaces = Lotacao.objects.filter(
            servidores_lotacao__designacao=True,
            servidores_lotacao__ativo=True,
            servidores_lotacao__servidor=self.employee,
        )

        q_workplaceconfigtag = WorkplaceConfigTag.objects.filter(
            tag="30",  # id: 30, label: EXERCÍCIO CUMULATIVO
            workplace__in=workplaces,
        )

        if q_workplaceconfigtag.exists() is False:
            raise self.CalculationNotApplicable(
                """
                O Membro não tem designação com lotação de exercício cumulativo ou a lotação está sem a TAG configurada para exercício cumulativo.
            """
            )

    def validate(self):
        self.validate_if_is_member()
        self.validate_if_workplace_has_cumulative_tag()

    @cached()
    def _exclude_ranges_for_range_salary(self, range_salary=None):
        if not range_salary:
            range_salary = self.range_salary

        range_unpaid_absences = NewDateRange()

        for mc in AfastamentoOutroOrgao.objects.filter(servidor=self.employee).exclude(
            Q(data_inicio__gt=range_salary.last)
            | Q(onus=1)
            | Q(transito_pela_folha=True)
            | Q(estado=AFASTAMENTO_CANCELADO)
        ):
            range_unpaid_absences += NewDateRange(mc.data_inicio, mc.data_fim)

        for absence in (
            BaseLicencaAfastamento.objects.filter(servidor=self.employee)
            .exclude(
                Q(data_fim__lt=range_salary.first)
                | Q(data_inicio__gt=range_salary.last)
            )
            .exclude(~Q(afastamento__afastamentooutroorgao=None))
            .exclude(estado=AFASTAMENTO_CANCELADO)
        ):
            range_unpaid_absences += NewDateRange(absence.data_inicio, absence.data_fim)

        return range_unpaid_absences


@RunCodeManager.register("gfp-mpmt-aid-cumulative-exercises-coord-sub")
class AidExtraCumulativeExercisesCoordSub(AidExtraCumulativeExercises):

    title = "Exercício Cumulativo de Substituição de Coordenação"

    TAG = "30"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        year = self.year
        month = self.month
        if self.payroll and self.payroll.folha_anterior:
            self.payroll = self.payroll.folha_anterior
            year = self.payroll.periodo.ano
            month = self.payroll.periodo.mes
        else:
            self.payroll = None

        self.range_salary = NewDateRange.from_month(year, (month if month < 12 else 12))

    def valida_folha_anterior(self):
        if not self.payroll.folha_anterior:
            raise Exception("A Folha atual não possui Folha Anterior configurada!")

    def get_works_assignment(self):
        query = self.employee.servidor_lotacao.filter(servidor=self.employee)
        query = query.exclude(
            Q(data_vigencia_inicio__gt=self.range_salary.last)
            | (
                ~Q(data_vigencia_fim=None)
                & Q(data_vigencia_fim__lt=self.range_salary.first)
            )
        )
        return query.filter(designacao=True, from_substitution=True).order_by(
            "-data_vigencia_inicio"
        )

    def validate_employee_workplace(self):
        workplaces = self.get_works_assignment()
        lotacoes = []
        for wp in workplaces:
            lotacoes.append(wp.lotacao)

        query = WorkplaceConfigTag.objects.filter(workplace__in=lotacoes)
        query = query.filter(tag=self.TAG)
        query = query.exclude(
            Q(start_validity__gt=self.range_salary.last)
            | (~Q(end_validity=None) & Q(end_validity__lt=self.range_salary.first))
        )

        if not query.exists():
            raise self.CalculationNotApplicable(
                f"WORKPLACE_TAG {self.TAG}: o Servidor não tem exercicio em lotação ou a lotação não tem a configuração!"
            )

    def validate(self):
        super().validate_if_is_member()
        self.valida_folha_anterior()
        self.validate_employee_workplace()

    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            try:
                return float(self.params["qnt"])
            except Exception:
                return self._base_value[1]
        else:
            designacoes = ServidorLotacao.objects.filter(
                servidor=self.employee,
                designacao=True,
                from_substitution=True,
                data_vigencia_inicio__lte=self.range_salary.last,
            ).filter(
                Q(data_vigencia_fim__isnull=True)
                | Q(data_vigencia_fim__gte=self.range_salary.first)
            )

            total_dias = 0
            range_desigs = []
            if designacoes.exists():
                for i, designacao in enumerate(designacoes):
                    dt_inicio = (
                        designacao.data_vigencia_inicio
                        if designacao.data_vigencia_inicio > self.range_salary.first
                        else self.range_salary.first
                    )
                    dt_fim = (
                        self.range_salary.last
                        if designacao.data_vigencia_fim is None
                        else designacao.data_vigencia_fim
                    )
                    range_desigs.append((dt_inicio, dt_fim))

                for x in NewDateRange.consolidate_ranges_of_date(range_desigs):
                    total_dias += NewDateRange(x[0], x[1]).days

            return total_dias

    def base_value(self):
        periodo = Periodo.objects.filter(ano=self.year, mes=self.month)
        if periodo.exists():
            base_value = periodo.first().salario_teto_membros
        else:
            base_value = (
                Periodo.objects.order_by("-ano", "-mes").first().salario_teto_membros
            )

        return float(base_value)


@RunCodeManager.register("gfp-mpmt-aid-asmip")
class AidExtraAsmip(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade ASMIP % - percentual"

    SLUG_EXTRA_PAYMENT_FOR_AID = "ASMIP"

    FILTER_EMPLOYEE = True

    FILTER_BY_TYPE = 2

    FULL_VALUE = False


@RunCodeManager.register("gfp-mpmt-aid-asmip-fixa")
class AidExtraAsmipFixa(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade ASMIP R$ - fixa"

    SLUG_EXTRA_PAYMENT_FOR_AID = "ASMIP"

    FILTER_EMPLOYEE = True

    FILTER_BY_TYPE = 1


@RunCodeManager.register("gfp-mpmt-aid-sicred-cota")
class AidExtraSicred(AidExtraPaymentBaseExtraPayment):

    title = "Sicred Cota % - percentual"

    SLUG_EXTRA_PAYMENT_FOR_AID = "SICRED-COTA"

    FILTER_EMPLOYEE = True

    FILTER_BY_TYPE = 2


@RunCodeManager.register("gfp-mpmt-aid-sicred-cota-fixa")
class AidExtraSicredCotaFixa(AidExtraPaymentBaseExtraPayment):

    title = "Sicred Cota R$ - fixa"

    SLUG_EXTRA_PAYMENT_FOR_AID = "SICRED-COTA"

    FILTER_EMPLOYEE = True

    FILTER_BY_TYPE = 1


@RunCodeManager.register("gfp-mpmt-aid-sindsemp")
class AidExtraSindsemp(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade Sindsemp"

    SLUG_EXTRA_PAYMENT_FOR_AID = "SINDSEMP"

    FILTER_EMPLOYEE = True

    FULL_VALUE = False

    RECALCULATE_BASES = 3


@RunCodeManager.register("gfp-mpmt-aid-ammp")
class AidExtraAmmp(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade AMMP"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AMMP"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-transport-allowance")
class AidExtraTransportAllowance(WorkDaysCalculation):

    title = "Ajuda de Custo para Transporte - Membros"

    SLUG_EXTRA_PAYMENT_FOR_AID = "AJUDA-CUSTO-TRANSP-MEMBROS"

    # FULL_VALUE = True

    IGNORE_DEPARTURE_REMUNERATE_FILTER = False

    RECALCULATE_BASES = 3

    def validate(self):
        self.validate_not_paycheck_pension()
        if self.employee.tipo != "M":
            raise self.CalculationNotApplicable(
                "Somente Membros tem direito a esta verba!"
            )

    @cached()
    def maximum_quantity(self):
        return self.range_salary_for().days

    @cached()
    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            log.debug(self.params["qnt"])
            return float(self.params["qnt"] or 0)
        else:
            qnt_range = self.range_salary_for()
            dep_days = self.departures_days()

            qtd = qnt_range.days - dep_days

            return 0 if qtd < 0 else qtd

    def _value_calc_normatized(self, calc, full_value=False):
        return self._get_value_from_calc(calc, full_value=full_value)

    def departures_days(self):
        """
        Método para buscar os afastamentos e dias em trabalho remoto do membro, que
        devem ser descontado da verba.
        Somente o tipo de afastamento Recesso não deve ser descontado.

        Somente descontar se o total de dias for maior ou igual a 15
        """

        qtd = 0
        for mc in AfastamentoOutroOrgao.objects.filter(servidor=self.employee).exclude(
            Q(data_inicio__gt=self.range_salary.last)
            | Q(onus=1)
            | Q(transito_pela_folha=True)
            | Q(estado=AFASTAMENTO_CANCELADO)
        ):
            mc_range = NewDateRange(mc.data_inicio, mc.data_fim)
            range_mc_intersection = mc_range.intersect(self.range_salary)
            if range_mc_intersection.days > 0:
                qtd += range_mc_intersection.days

        for absence in (
            BaseLicencaAfastamento.objects.filter(servidor=self.employee)
            .exclude(
                Q(data_fim__lt=self.range_salary.first)
                | Q(data_inicio__gt=self.range_salary.last)
            )
            .exclude(~Q(afastamento__afastamentooutroorgao=None))
            .exclude(
                tipo=7,  # ignorar tipo de afastamento Recesso
            )
            .exclude(estado=AFASTAMENTO_CANCELADO)
        ):
            abscence_range = NewDateRange(absence.data_inicio, absence.data_fim)
            range_abscence_intersection = abscence_range.intersect(self.range_salary)
            if range_abscence_intersection.days > 0:
                qtd += range_abscence_intersection.days

        range_remote = NewDateRange()
        for remote_work in MembersTelecommuting.objects.filter(
            employee=self.employee
        ).exclude(
            Q(data_fim__lt=self.range_salary.first)
            | Q(data_inicio__gt=self.range_salary.last)
        ):
            range_remote = NewDateRange(remote_work.data_inicio, remote_work.data_fim)
            range_remote_intersection = range_remote.intersect(self.range_salary)
            if range_remote_intersection.days > 0:
                qtd += range_remote_intersection.days

        return self.maximum_quantity() if qtd >= 15 else 0

    def base_value(self):
        periodo = Periodo.objects.filter(ano=self.year, mes=self.month)
        if periodo.exists():
            base_value = periodo.first().salario_teto_membros
        else:
            base_value = (
                Periodo.objects.order_by("-ano", "-mes").first().salario_teto_membros
            )

        return float(base_value)


@RunCodeManager.register("gfp-mpmt-aid-capemisa")
class AidExtraCapemisa(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade CAPEMISA"

    SLUG_EXTRA_PAYMENT_FOR_AID = "CAPEMISA"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-mongeralseguros")
class AidExtraMongeralSeguros(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade  MONGERAL SEGUROS"

    SLUG_EXTRA_PAYMENT_FOR_AID = "MONGERAL-SEGUROS"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-sicredi-confraria-juri")
class AidExtraSicrediConfrariaJuri(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade  SICRED-CONFRARIA-JURI"

    SLUG_EXTRA_PAYMENT_FOR_AID = "SICRED-CONFRARIA-JURI"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-fessp")
class AidExtraFessp(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade  FESSP"

    SLUG_EXTRA_PAYMENT_FOR_AID = "FESSP"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-mbm-seguro")
class AidExtraSecureMBM(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade MBM Seguro"

    SLUG_EXTRA_PAYMENT_FOR_AID = "MENSALIDADE-MBM-SEGURO"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-petalozzi-cuiaba")
class AidExtraPestalozziCuiaba(AidExtraPaymentBaseExtraPayment):

    title = "CONTRIBUICAO ASSOC. PESTALOZZI CUIABA"

    SLUG_EXTRA_PAYMENT_FOR_AID = "PESTALOZZI-CUIABA"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-fespmp")
class AidExtraFespmp(AidExtraPaymentBaseExtraPayment):

    title = "Mensalidade FESPMP"

    SLUG_EXTRA_PAYMENT_FOR_AID = "FESPMP"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True


@RunCodeManager.register("gfp-mpmt-aid-diligence-transport")
class AidDiligenceTransport(AidExtraPaymentBaseExtraPayment):

    title = "Diligência"

    SLUG_EXTRA_PAYMENT_FOR_AID = "VERBA_DILIGENCIA"

    FILTER_EMPLOYEE = True

    WITHOUT_DAYS = True

    holder_diligences = None
    substitute_diligences = None
    extra_payment = None

    def get_possessions_by_type(self, types=[]):
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

    def get_salaries(self, cargo_recebe):
        salaries = EstruturaTabelaSalarial.salarios(
            cargo_recebe, self.payroll.date_range.first, self.payroll.date_range.last
        )

        return salaries[0][1]

    def get_diligences(self):
        return MovimentacaoDiligencia.objects.filter(
            Q(data_inicio__gte=self.payroll.date_range.first)
            | Q(data_fim__gt=self.payroll.date_range.first)
            | Q(data_fim__isnull=True)
        )

    def get_holder_diligences(self):
        holder_ranges = []
        for dilig in self.get_diligences().filter(servidor=self.employee):
            holder_ranges.append(
                NewDateRange.range_intersect(
                    [
                        dilig.data_inicio,
                        (
                            self.payroll.date_range.last
                            if dilig.data_fim is None
                            else dilig.data_fim
                        ),
                    ],
                    [self.payroll.date_range.first, self.payroll.date_range.last],
                )
            )

        return holder_ranges

    def get_substitute_diligences(self):
        mes_anterior = self.payroll.date_range.first - relativedelta(months=1)
        dt_range_mes_anterior = NewDateRange.from_month(
            mes_anterior.year, mes_anterior.month
        )
        mes_anterior_inicio = dt_range_mes_anterior.first
        mes_anterior_fim = dt_range_mes_anterior.last

        substitute_ranges = []
        for dilig in self.get_diligences().filter(substituto=self.employee):
            if dilig.data_inicio < self.payroll.date_range.first:
                dt_inicio_range = self.payroll.date_range.first
            else:
                dt_inicio_range = dilig.data_inicio

            if dilig.data_fim is None or dilig.data_fim > self.payroll.date_range.last:
                dt_fim_range = self.payroll.date_range.last
            else:
                dt_fim_range = dilig.data_fim

            if dt_fim_range > dt_inicio_range:
                departures_holder = self._exclude_ranges_for_range_salary(
                    range_salary=NewDateRange(mes_anterior_inicio, mes_anterior_fim),
                    employee=dilig.servidor,
                )
                for dep_holder in departures_holder._ranges:
                    substitute_ranges.append(
                        NewDateRange.range_intersect(
                            [mes_anterior_inicio, mes_anterior_fim],
                            [dep_holder[0], dep_holder[1]],
                        )
                    )

        return substitute_ranges

    def _exclude_ranges_for_range_salary(self, range_salary=None, employee=None):
        if employee is None:
            employee = self.employee

        if not range_salary:
            range_salary = self.range_salary

        mes_anterior = self.payroll.date_range.first - relativedelta(months=1)
        dt_range_mes_anterior = NewDateRange.from_month(
            mes_anterior.year, mes_anterior.month
        )
        mes_anterior_inicio = dt_range_mes_anterior.first
        mes_anterior_fim = dt_range_mes_anterior.last

        # IDs dos afastamentos que não devem ser descontados
        # ID: 63 - Licença Saúde de Horas
        ids_afast_exclude = [63]

        range_unpaid_absences = NewDateRange()
        if self.IGNORE_DEPARTURE is False:
            for mc in AfastamentoOutroOrgao.objects.filter(servidor=employee).exclude(
                Q(data_inicio__gt=mes_anterior_fim)
                | Q(onus=1)
                | Q(transito_pela_folha=True)
                | Q(estado=AFASTAMENTO_CANCELADO)
            ):
                range_unpaid_absences += NewDateRange(mc.data_inicio, mc.data_fim)
            for absence in (
                BaseLicencaAfastamento.objects.filter(servidor=employee)
                .exclude(
                    Q(data_fim__lt=mes_anterior_inicio)
                    | Q(data_inicio__gt=mes_anterior_fim)
                )
                .exclude(~Q(afastamento__afastamentooutroorgao=None))
                .exclude(
                    estado=AFASTAMENTO_CANCELADO,
                    tipo__in=ids_afast_exclude,
                )
            ):
                range_unpaid_absences += NewDateRange(
                    absence.data_inicio, absence.data_fim
                )

        return range_unpaid_absences

    def quantity(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            return float(self.params["qnt"] or 0)
        else:
            days = 0
            if self.holder_diligences or self.substitute_diligences:
                exclude_ranges = self._exclude_ranges_for_range_salary()
                if self.holder_diligences:
                    for holder_range in self.holder_diligences:
                        date_range = NewDateRange(holder_range[0], holder_range[1])
                        days += date_range.days

                if self.substitute_diligences:
                    for substitute_range in self.substitute_diligences:
                        date_range = NewDateRange(
                            substitute_range[0], substitute_range[1]
                        )
                        days += date_range.days

            return days - exclude_ranges.days

    def _query_extra_payments(self):
        q = ExtraPaymentPeriod.objects.filter(
            employee=None, extra_payment__slug=self.SLUG_EXTRA_PAYMENT_FOR_AID
        ).filter(
            models.Q(start_validity__lte=self.payroll.date_range.first)
            & (
                models.Q(end_validity=None)
                | models.Q(end_validity__gte=self.payroll.date_range.first)
            )
        )

        self.extra_payment = q
        return q

    def base_value(self):
        q = self.extra_payment
        return round(float(q[0].value), 2) if q.exists() else 10.00

    def validate_if_employee_in_diligence(self):
        if not MovimentacaoDiligencia.objects.filter(
            Q(servidor=self.employee) | Q(substituto=self.employee)
        ).exists():
            raise self.CalculationNotApplicable(
                "O Servidor não está em Designação para Diligência!"
            )

    def validate_if_has_diligence_in_payroll_period(self):
        self.holder_diligences = self.get_holder_diligences()
        self.substitute_diligences = self.get_substitute_diligences()
        if self.holder_diligences is None and self.substitute_diligences is None:
            raise self.CalculationNotApplicable(
                f"""
            O Servidor não tem período de Designação para Diligência em concomitância com o período da folha: {self.payroll}!
            """
            )

    def validate(self):
        self.validate_if_employee_in_diligence()
        self.validate_if_has_diligence_in_payroll_period()
