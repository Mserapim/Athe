# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models

from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.ferias.models import PeriodoAquisitivoServidor
from rh.gfp.calcs.mpto.ferias import BaseVacation
from rh.gfp.calcs.mpto.remuneracao import ChristmasGratification
from rh.gfp.calcs.mpto.socialsecurity import BaseSocialSecurity
from rh.gfp.models import Folha as Payroll
from rh.gfp.models import FolhaEvento as Entry
from rh.gfp.planoconta.models import ProvisionManager, ProvisionPlan
from rh.gfp.signals.regime_previdenciario import get_regime_previdenciario
from rh.models import Servidor as Employee
from standard.models import Choice, RunCodeManager

log = getLogger(__name__)


class ProvisionGenerator(object):

    title = "Gerador Base para provisões"
    typeof = "PROV-GENERATOR"

    class CreatePeriodsNotImplemented(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                'ERRO - Informe os desenvolvedores do sistema: O método "create_periods" deve ser implementado na\
                    classe especializada, para criar os períodos(provisions) de cada servidor',
            )

    class ClosedPeriod(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Período fechado e por isso não pode ser alterado!"
            )

    def __init__(self, year, month, type_provision, pension_system=None, task=None):
        self.provision_plan = ProvisionPlan.objects.get(type_provision=type_provision)
        self.year = year
        self.month = month
        self.cutting_date = date(self.year, self.month, 15)
        self.task = task
        self.pension_system = pension_system

    # @classmethod
    # def create_periods(self):
    #     raise self.CreatePeriodsNotImplemented()


# @RunCodeManager.register('gfp-mpto-provision-13thsalary')
class ChristmasGratificationProvision(ChristmasGratification):

    title = "Provisão de 13° Salário"
    typeof = "PROVISION"

    def base_socialsecurity(self, total=False):
        """
        Este calculo deve ser sobrescrito para todo calculo que
        se deseja saber a base previdenciária utilizada pelo calculo
        """
        return self.value()


# @RunCodeManager.register('gfp-mpto-provision-socialsecurity')
class ProvisionSocialSecurity(BaseSocialSecurity):
    title = "Provisão de Previdencia (patronal)"
    typeof = "PROVISION"

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "base_value"]

    def get_pj(self):
        try:
            pj = get_regime_previdenciario(self.employee, self.range_salary)
        except Exception as e:
            log.exception(e)
            pj = None
        finally:
            return pj

    def validate(self):
        self.validate_not_paycheck_pension()
        # log.debug("PREVIDENCIA %s" % self.get_pj())
        if not self.get_pj():
            raise self.CalculationNotApplicable(
                "O servidor não possui um regime previdenciário!"
            )
        if self.get_pj() != self.inss:
            raise self.CalculationNotApplicable(
                "Cálculo não aplicável à previdenica %s" % self.get_pj()
            )


@RunCodeManager.register("gfp-mpto-provision-socialsecurity-christmas")
class ProvisionSocialSecurityChristmas(ProvisionSocialSecurity):
    title = "Provisão de Previdencia para 13̣°̣ Salário (patronal)"
    typeof = "PROVISION"

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = ["info", "base_value"]

    def validate(self):
        # log.debug("PREVIDENCIA %s" % self.get_pj())
        if not self.get_pj():
            raise self.CalculationNotApplicable(
                "O servidor não possui um regime previdenciário!"
            )


@RunCodeManager.register("gfp-mpto-provision-vacation")
class VacationProvision(BaseVacation):

    title = "Provisão de Férias"
    typeof = "PROVISION"

    MULTI_CALCULATE = False

    @property
    @cache_return
    def object(self):
        cutting_date = date(self.year, self.month, 15)
        pas = None
        try:
            pas = self.employee.periodos_aquisitivos.get(
                data_inicio_aquisicao__lte=cutting_date,
                data_fim_aquisicao__gte=cutting_date,
            )
        finally:
            return pas

    def percentage(self):
        if not self.object:
            return 0.00
        return (
            33.3333333333
            if self.object.pas.periodo_aquisitivo.ano_aquisicao < 2012
            else 50.0
        )

    def event_information(self):
        return "%s" % self.object.pas.periodo_aquisitivo

    def base_socialsecurity(self, total=False):
        """
        Este calculo deve ser sobrescrito para todo calculo que
        se deseja saber a base previdenciária utilizada pelo calculo
        """
        return self.value()

    def maximum_quantity(self):
        return 1.0


class VacationGenerator(ProvisionGenerator):

    title = "Gerador para Provisões de Férias"

    class BasePayrollNotFound(Exception):
        def __init__(self):
            Exception.__init__(
                self, "A folha base não foi encontrada ou não está processada/fechada!"
            )

    def create_period_for_employee(self, provision_manager, employee, task=None):
        # print '%-60s:%10s:%10s:' % (employee, employee.data_exercicio, employee.data_desligamento or ''),
        pas = None
        try:
            pas = employee.periodos_aquisitivos.get(
                data_inicio_aquisicao__lte=self.cutting_date,
                data_fim_aquisicao__gte=self.cutting_date,
            )
        except PeriodoAquisitivoServidor.DoesNotExist:
            # NOTIFY
            # print 'PROVISION HOLIDAYS does not have PAS'
            # log.debug('PROVISION HOLIDAYS does not have PAS')
            if task:
                task.info("%s - Não possui periodo aquisitivo vigente." % employee)
        except PeriodoAquisitivoServidor.MultipleObjectsReturned:
            # print 'Periodos aquisitivos conflitando.'
            # log.debug('Períodos aquisitivos conflitando.')
            if task:
                task.info(
                    "%s - possui periodos arquisitivos conflitando." % employee, 2
                )
        except Exception as e:
            # log.debug(e)
            task.info("Erro ao criar periodo: %s" % e)
        else:

            paid_events_value_ids = [
                ev.pk for ev in self.provision_plan.paid_events_value.all()
            ]
            # paid_events_employer_ids = [ev.pk for ev in self.provision_plan.paid_events_employer.all()]

            pe, created = self.provision_plan.provisions_employee.get_or_create(
                employee=employee,
                info="%s" % pas.periodo_aquisitivo,
                defaults={
                    "start_acquisition": pas.data_inicio_aquisicao,
                    "end_acquisition": pas.data_fim_aquisicao,
                    "quantity": 12
                    / pas.periodo_aquisitivo.configuracao.quantidade_periodos,
                },
            )
            if not created:
                pe.start_acquisition = pas.data_inicio_aquisicao
                pe.end_acquisition = pas.data_fim_aquisicao
                pe.quantity = (
                    12 / pas.periodo_aquisitivo.configuracao.quantidade_periodos
                )
                pe.save()

            is_first_provision = (
                not pe.provisions.exclude(
                    provision_manager__reference_year__gt=provision_manager.reference_year
                )
                .exclude(
                    provision_manager__reference_year=provision_manager.reference_year,
                    provision_manager__reference_month__gte=provision_manager.reference_month,
                )
                .exists()
            )
            dt_rel = (
                date(
                    pas.data_inicio_aquisicao.year, pas.data_inicio_aquisicao.month, 15
                )
                if is_first_provision
                else date(self.year, self.month, 15)
            )
            # is_first_provision_of_employee = (dt_rel == date(
            #     pas.data_inicio_aquisicao.year, pas.data_inicio_aquisicao.month, 15))
            if is_first_provision and dt_rel < pe.start_acquisition:
                dt_rel += relativedelta(months=1)

            if pe.start_acquisition <= dt_rel <= pe.end_acquisition:
                prov, created = pe.provisions.get_or_create(
                    provision_manager=provision_manager
                )
                prov.provisioned_value = 0.0
                prov.paid_value = 0.0
                prov.provisioned_employer = 0.0
                prov.paid_employer = 0.0
                prov.previous_balance_value = 0.0
                prov.previous_balance_employer = 0.0
                prov.manual_balance_value = 0.0
                prov.manual_balance_employer = 0.0
                prov.acquired = 0

                qnt_unpaid = (
                    employee.periodos_aquisitivos.exclude(
                        models.Q(pago_sem_folha=True) | models.Q(bloqueado=True)
                    )
                    .filter(
                        models.Q(data_fim_aquisicao__lt=pe.start_acquisition)
                        & (
                            models.Q(folha_evento_terco_constitucional=None)
                            | models.Q(
                                folha_evento_terco_constitucional__folha__periodo__ano__gt=dt_rel.year
                            )
                            | (
                                models.Q(
                                    folha_evento_terco_constitucional__folha__periodo__ano=dt_rel.year
                                )
                                & models.Q(
                                    folha_evento_terco_constitucional__folha__periodo__mes__gte=dt_rel.month
                                )
                            )
                        )
                    )
                    .count()
                )

                while dt_rel <= min(pe.end_acquisition, self.cutting_date):
                    payroll = Payroll.objects.get(
                        periodo__ano=dt_rel.year,
                        periodo__mes=dt_rel.month,
                        tipo_folha__principal=True,
                    )
                    # print '>>> %02d/%04d %040s' % (dt_rel.month, dt_rel.year, payroll),

                    prov.acquired += 1
                    q_events = Entry.objects.filter(
                        contracheque__servidor=pe.employee,
                        evento__pk__in=paid_events_value_ids,
                    )
                    calc_prov = VacationProvision(employee, payroll).calculate()
                    prov.provisioned_value += calc_prov.get("valor", 0.00) / pe.quantity
                    # print round(prov.provisioned_value, 2),
                    calc_ss_prov = ProvisionSocialSecurity(
                        employee, payroll, params={"base_value": prov.provisioned_value}
                    ).calculate()
                    prov.base_salary = calc_prov.get("valor_base", 0.00)
                    prov.provisioned_employer = calc_ss_prov.get("patronal", 0.00)
                    if prov.previous:
                        prov.previous_balance_value = prov.previous.balance_value
                        prov.previous_balance_employer = prov.previous.balance_employer
                    else:
                        if dt_rel == date(
                            pe.start_acquisition.year, pe.start_acquisition.month, 15
                        ):
                            prov.previous_balance_value = (
                                prov.previous_balance_employer
                            ) = 0.0
                            if (
                                pas.pago
                                and pas.folha_evento_terco_constitucional
                                and pas.folha_evento_terco_constitucional.folha.periodo
                                < payroll.periodo
                            ):
                                calc_ss_prev = ProvisionSocialSecurity(
                                    employee,
                                    pas.folha_evento_terco_constitucional.folha,
                                    params={
                                        "base_value": calc_prov.get(
                                            "base_previdencia", 0.00
                                        )
                                    },
                                ).calculate()
                                prov.previous_balance_value = (
                                    float(pas.folha_evento_terco_constitucional.valor)
                                    * -1
                                )
                                prov.previous_balance_employer = (
                                    calc_ss_prev.get("patronal", 0.00) * -1
                                )

                    q_events_paid = q_events.filter(
                        contracheque__folha__periodo__ano=dt_rel.year,
                        contracheque__folha__periodo__mes=dt_rel.month,
                    )
                    total_values = (
                        q_events_paid.aggregate(value=models.Sum("value"))["value"]
                        or 0.00
                    )
                    calc_ss_paid = ProvisionSocialSecurity(
                        employee, payroll, params={"base_value": total_values}
                    ).calculate()
                    total_employer = calc_ss_paid.get("patronal", 0.00)
                    prov.paid_value += float(total_values) * -1
                    prov.paid_employer += float(total_employer) * -1
                    dt_rel += relativedelta(months=1)

                if prov.is_first_provision or (
                    pe.provision_plan.update_previous_balance
                    and prov.is_first_provision_of_manager
                ):
                    calc_prev_prov = VacationProvision(employee, payroll).calculate()
                    calc_ss = ProvisionSocialSecurity(
                        employee,
                        payroll,
                        params={"base_value": calc_prev_prov.get("valor", 0.00)},
                    ).calculate()
                    if prov.is_first_provision:
                        prov.previous_balance_value = (
                            calc_prev_prov.get("valor", 0.00) * qnt_unpaid
                        )
                        prov.previous_balance_employer = (
                            calc_ss.get("patronal", 0.00) * qnt_unpaid
                        )
                    else:
                        prov.manual_balance_value = (
                            calc_prev_prov.get("valor", 0.00) * qnt_unpaid
                            - prov.previous_balance_value
                        )
                        prov.manual_balance_employer = (
                            calc_ss.get("patronal", 0.00) * qnt_unpaid
                            - prov.previous_balance_employer
                        )

                prov.save()
            else:
                # log.debug('NOT IN PERIOD...')
                # print 'NOT IN PERIOD...'
                if task:
                    task.info("%s - não está no periodo" % employee)

    def create_periods(self, employers=[], task=None):

        pension_system = (
            self.pension_system
            if self.pension_system
            else [
                ch.value
                for ch in Choice.objects.filter(
                    app_label="rh", name="REGIME_PREVIDENCIARIO"
                )
            ]
        )
        # log.debug(pension_system)
        for ps in pension_system:
            base_payroll = Payroll.objects.filter(
                tipo_folha__principal=True,
                status__in=[3, 4],
                periodo__ano=self.year,
                periodo__mes=self.month,
            ).last()
            if not base_payroll:
                raise self.BasePayrollNotFound()

            q_employers = Employee.objects.filter(
                paychecks__folha__periodo__ano=self.year,
                paychecks__folha__periodo__mes=self.month,
                regime_previdenciario=ps,
            ).annotate(lancamentos=models.Count("paychecks"))

            if employers:
                q_employers = q_employers.filter(matricula__in=employers)

            # cutting_date = date(self.year, self.month, 15)

            prov_manager, created = ProvisionManager.objects.get_or_create(
                provision_plan=self.provision_plan,
                reference_year=self.year,
                reference_month=self.month if self.month != 13 else 12,
                pension_system=ps,
            )

            if not created and prov_manager.status in [3, 4]:
                raise self.ClosedPeriod()

            if task:
                task["total"] = q_employers.count()
                count = 0

            for e in q_employers:
                # for cc in q_cc:
                self.create_period_for_employee(prov_manager, e, task)
                if task:
                    count += 1
                    task["pct"] = count

            total = prov_manager.provisions.aggregate(
                total_provisioned_value=models.Sum("provisioned_value"),
                total_paid_value=models.Sum("paid_value"),
                total_provisioned_employer=models.Sum("provisioned_employer"),
                total_paid_employer=models.Sum("paid_employer"),
                total_previous_balance_value=models.Sum("previous_balance_value"),
                total_previous_balance_employer=models.Sum("previous_balance_employer"),
                total_manual_balance_value=models.Sum("manual_balance_value"),
                total_manual_balance_employer=models.Sum("manual_balance_employer"),
            )

            prov_manager.total_provisioned_value = total["total_provisioned_value"]
            prov_manager.total_paid_value = total["total_paid_value"]
            prov_manager.total_provisioned_employer = total[
                "total_provisioned_employer"
            ]
            prov_manager.total_paid_employer = total["total_paid_employer"]
            prov_manager.total_previous_balance_value = total[
                "total_previous_balance_value"
            ]
            prov_manager.total_previous_balance_employer = total[
                "total_previous_balance_employer"
            ]
            prov_manager.total_manual_balance_value = total[
                "total_manual_balance_value"
            ]
            prov_manager.total_manual_balance_employer = total[
                "total_manual_balance_employer"
            ]
            prov_manager.pension_system = ps

            prov_manager.save()


class ChristmasGenerator(ProvisionGenerator):

    title = "Gerador para Provisões de 13º salário"

    class BasePayrollNotFound(Exception):
        def __init__(self):
            Exception.__init__(
                self, "A folha base não foi encontrada ou não está processada/fechada!"
            )

    def create_period_for_employee(self, provision_manager, employee, task=None):
        # print '%-60s:%10s:%10s:' % (employee, employee.data_exercicio, employee.data_desligamento or ''),

        data_inicio_aquisicao = (
            employee.data_exercicio
            if employee
            and employee.data_exercicio > date(provision_manager.reference_year, 1, 1)
            else date(provision_manager.reference_year, 1, 1)
        )
        data_fim_aquisicao = (
            date(provision_manager.reference_year, 12, 31)
            if not employee.data_desligamento
            else employee.data_desligamento
        )

        paid_events_value_ids = [
            ev.pk for ev in self.provision_plan.paid_events_value.all()
        ]
        # paid_events_employer_ids = [ev.pk for ev in self.provision_plan.paid_events_employer.all()]

        pe, created = self.provision_plan.provisions_employee.get_or_create(
            employee=employee,
            info="ANO: %s" % provision_manager.reference_year,
            defaults={
                "start_acquisition": data_inicio_aquisicao,
                "end_acquisition": data_fim_aquisicao,
                "quantity": 12,
            },
        )
        if not created:
            pe.start_acquisition = data_inicio_aquisicao
            pe.end_acquisition = data_fim_aquisicao
            pe.quantity = 12
            pe.save()

        is_first_provision = (
            not pe.provisions.exclude(
                provision_manager__reference_year__gt=provision_manager.reference_year
            )
            .exclude(
                provision_manager__reference_year=provision_manager.reference_year,
                provision_manager__reference_month__gte=provision_manager.reference_month,
            )
            .exists()
        )
        dt_rel = (
            date(data_inicio_aquisicao.year, data_inicio_aquisicao.month, 15)
            if is_first_provision
            else date(self.year, self.month, 15)
        )

        if is_first_provision and dt_rel < pe.start_acquisition:
            dt_rel += relativedelta(months=1)

        # log.debug('SERVIDOR: %s DTREL %s INICIO %s FIM %s' %
        #           (employee, dt_rel, pe.start_acquisition, pe.end_acquisition))

        if (
            dt_rel.month <= provision_manager.reference_month
            and dt_rel.year
            == provision_manager.reference_year
            == pe.end_acquisition.year
        ):
            daterange_rel = NewDateRange.from_month(dt_rel.year, dt_rel.month)
            daterange_acquisition = NewDateRange(
                data_inicio_aquisicao, data_fim_aquisicao
            )
            prov, created = pe.provisions.get_or_create(
                provision_manager=provision_manager
            )
            prov.provisioned_value = 0.0
            prov.paid_value = 0.0
            prov.provisioned_employer = 0.0
            prov.paid_employer = 0.0
            prov.previous_balance_value = 0.0
            prov.previous_balance_employer = 0.0
            prov.manual_balance_value = 0.0
            prov.manual_balance_employer = 0.0
            prov.acquired = 0

            # while dt_rel <= min(pe.end_acquisition, self.cutting_date):
            dt_while = daterange_rel.intersect(daterange_acquisition).days
            # while dt_rel.month <= min(pe.end_acquisition.month, self.cutting_date.month):
            while dt_rel.month <= provision_manager.reference_month:
                # log.debug('AAAA %s %s %s' % (daterange_acquisition, daterange_rel, dt_while))
                acquired = 1 if dt_while >= 15 else 0
                # log.debug('AAAA %02d/%04d' % (dt_rel.month, dt_rel.year))
                payroll = Payroll.objects.get(
                    periodo__ano=dt_rel.year,
                    periodo__mes=dt_rel.month,
                    tipo_folha__principal=True,
                )

                if (dt_rel.month <= pe.end_acquisition.month) and (
                    dt_rel.month >= pe.start_acquisition.month
                ):
                    prov.acquired += acquired
                    calc_prov = ChristmasGratificationProvision(
                        employee, payroll
                    ).calculate()
                    prov.provisioned_value += (
                        calc_prov.get("valor_base", 0.00) / pe.quantity
                    ) * acquired
                    # print round(prov.provisioned_value, 2),
                    calc_ss_prov = ProvisionSocialSecurityChristmas(
                        employee, payroll, params={"base_value": prov.provisioned_value}
                    ).calculate()
                    prov.base_salary = calc_prov.get("valor_base", 0.00)
                    prov.provisioned_employer = calc_ss_prov.get("patronal", 0.00)

                if prov.previous:
                    prov.previous_balance_value = prov.previous.balance_value
                    prov.previous_balance_employer = prov.previous.balance_employer
                else:
                    if dt_rel == date(
                        pe.start_acquisition.year, pe.start_acquisition.month, 15
                    ):
                        prov.previous_balance_value = prov.previous_balance_employer = (
                            0.0
                        )

                q_events = Entry.objects.filter(
                    contracheque__servidor=pe.employee,
                    evento__pk__in=paid_events_value_ids,
                    reference_year=dt_rel.year,
                )
                q_events_paid = q_events.filter(
                    contracheque__folha__periodo__ano=dt_rel.year,
                    contracheque__folha__periodo__mes=dt_rel.month,
                )
                total_values = (
                    q_events_paid.aggregate(value=models.Sum("value"))["value"] or 0.00
                )
                calc_ss_paid = ProvisionSocialSecurityChristmas(
                    employee, payroll, params={"base_value": total_values}
                ).calculate()
                total_employer = calc_ss_paid.get("patronal", 0.00)
                prov.paid_value += float(total_values) * -1
                # log.debug('AAA PAID VALUE: %s DTREL %s' % (prov.paid_value, dt_rel))
                prov.paid_employer += float(total_employer) * -1
                dt_rel += relativedelta(months=1)

                if prov.is_first_provision or (
                    pe.provision_plan.update_previous_balance
                    and prov.is_first_provision_of_manager
                ):
                    calc_prev_prov = ChristmasGratificationProvision(
                        employee, payroll
                    ).calculate()
                    calc_ss = ProvisionSocialSecurityChristmas(
                        employee,
                        payroll,
                        params={"base_value": calc_prev_prov.get("valor", 0.00)},
                    ).calculate()
                    if prov.is_first_provision:
                        prov.previous_balance_value = 0
                        prov.previous_balance_employer = 0
                    else:
                        prov.manual_balance_value = (
                            calc_prev_prov.get("valor", 0.00)
                            - prov.previous_balance_value
                        )
                        prov.manual_balance_employer = (
                            calc_ss.get("patronal", 0.00)
                            - prov.previous_balance_employer
                        )
                        # log.debug('AAAA BALANCE: %s' % prov.manual_balance_value)

                # log.debug('AAAA DT_WHILE AAAA: %s' % dt_rel)
                # log.debug(daterange_acquisition)
                dt_while = (
                    NewDateRange.from_month(dt_rel.year, dt_rel.month)
                    .intersect(daterange_acquisition)
                    .days
                )
                # log.debug('AAAA DT_WHILE: %s' % dt_while)
            prov.save()
        else:
            # log.debug('NOT IN PERIOD...')
            # print 'NOT IN PERIOD...'
            if task:
                task.info("%s - não está no periodo" % employee)

    def create_periods(self, employers=[], task=None):

        pension_system = (
            self.pension_system
            if self.pension_system
            else [
                ch.value
                for ch in Choice.objects.filter(
                    app_label="rh", name="REGIME_PREVIDENCIARIO"
                )
            ]
        )

        for ps in pension_system:
            base_payroll = Payroll.objects.filter(
                tipo_folha__principal=True,
                status__in=[3, 4],
                periodo__ano=self.year,
                periodo__mes=self.month,
            ).last()
            if not base_payroll:
                raise self.BasePayrollNotFound()

            q_employers = Employee.objects.filter(
                paychecks__folha__periodo__ano=self.year,
                paychecks__folha__periodo__mes=self.month,
                regime_previdenciario=ps,
            ).annotate(lancamentos=models.Count("paychecks"))

            if employers:
                q_employers = q_employers.filter(matricula__in=employers)

            # cutting_date = date(self.year, self.month, 15)

            prov_manager, created = ProvisionManager.objects.get_or_create(
                provision_plan=self.provision_plan,
                reference_year=self.year,
                reference_month=self.month if self.month != 13 else 12,
                pension_system=ps,
            )

            if not created and prov_manager.status in [3, 4]:
                raise self.ClosedPeriod()

            if task:
                task["total"] = q_employers.count()
                count = 0

            for e in q_employers:
                # for cc in q_cc:
                self.create_period_for_employee(prov_manager, e, task)
                if task:
                    count += 1
                    task["pct"] = count

            total = prov_manager.provisions.aggregate(
                total_provisioned_value=models.Sum("provisioned_value"),
                total_paid_value=models.Sum("paid_value"),
                total_provisioned_employer=models.Sum("provisioned_employer"),
                total_paid_employer=models.Sum("paid_employer"),
                total_previous_balance_value=models.Sum("previous_balance_value"),
                total_previous_balance_employer=models.Sum("previous_balance_employer"),
                total_manual_balance_value=models.Sum("manual_balance_value"),
                total_manual_balance_employer=models.Sum("manual_balance_employer"),
            )

            prov_manager.total_provisioned_value = total["total_provisioned_value"]
            prov_manager.total_paid_value = total["total_paid_value"]
            prov_manager.total_provisioned_employer = total[
                "total_provisioned_employer"
            ]
            prov_manager.total_paid_employer = total["total_paid_employer"]
            prov_manager.total_previous_balance_value = total[
                "total_previous_balance_value"
            ]
            prov_manager.total_previous_balance_employer = total[
                "total_previous_balance_employer"
            ]
            prov_manager.total_manual_balance_value = total[
                "total_manual_balance_value"
            ]
            prov_manager.total_manual_balance_employer = total[
                "total_manual_balance_employer"
            ]
            prov_manager.pension_system = ps

            prov_manager.save()
