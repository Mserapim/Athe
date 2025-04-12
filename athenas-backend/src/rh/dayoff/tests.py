# -.- coding: utf-8 -.-
from django.template.defaultfilters import default
from rh.dayoff.signals.departure import manager_usufruct
from edocs.protocolo.models import Attachment
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from rh.afastamento.models import (
    AfastamentoOutroOrgao,
    FeriasAfastamento,
    Recesso,
    FolgaEleitoral,
    LicencaSaudeJuntaMedica,
    DEFERIDA,
)
from django.db.models import Q, Count

from dateutil.relativedelta import relativedelta
from mixer.backend.django import mixer

from contrib.middleware import set_current_user, get_current_user
from contrib.daterange import NewDateRange
from contrib.utils import employee_from_user
from engine.notification.models import Notification
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import (
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
    Servidor,
    Publicacao,
    ServidorLotacao,
    Prorrogacao,
    Lotacao,
)
from rh.const import ACTIVE, CANCELED, SCHEDULED, FINISHED
from rh.dayoff.models import (
    AcquisitionPeriod,
    Usufruct,
    Activity,
    Configuration,
    GroupPeriod,
    ActivityBook,
    ActivityInterrupt,
    Attachment,
)
from .const import (
    ACQP_PROGRESS,
    USU_ENJOYED,
    USU_HOMOLOGATED,
    USU_AUTORIZED_CI,
    ACQP_WAIT,
    CONFIGURATION_CHOICE,
    CONF_VACATION,
    CONF_RECESS,
    CONF_BIRTHDAY_BREAK,
    CONF_COMPENSATION,
    CONF_DUTTY,
    CONF_ELECTORAL_SLACK,
    AUTO_HOMOLOGATION,
    AUTO_HOMOLOGATION_NOT,
    USU_NEW,
    ACT_ST_AUTHORIZED_M,
    ACT_ST_AUTHORIZED,
    USU_CANCELED,
    AUTO_HOMOLOGATION_AFTER_SCALE,
    USU_ENJOYING,
)
from standard.models import Choice, ClassCode
from engine.mq.models import Task

import datetime
import unittest
import time

set_current_user("iradianmorais")

VERBOSE = False

year = (datetime.datetime.now() - relativedelta(years=1)).date().year
start_date_acquisition = datetime.datetime(year, 1, 26).date()
end_date_acquisition = start_date_acquisition + relativedelta(years=1)
start_date_book = datetime.datetime(year, 10, 1).date()
end_date_book = datetime.datetime(year, 10, 30).date()
year_reference_vacation_begin = start_date_acquisition.year
year_reference_vacation = end_date_acquisition.year

start_date_fruition = end_date_acquisition
end_date_fruition = start_date_acquisition + relativedelta(years=5)


def delete_all():
    delete_employee(79107)
    delete_employee(75207)
    delete_employee(4191)
    delete_employee(68507)
    delete_employee(67807)
    delete_employee(6791)
    delete_employee(87708)
    # BaseLicencaAfastamento.atualizar_estado = lambda x: True
    # ServidorLotacao.call_update_from_departure = lambda x: True
    # print('delete_all start...')
    # Notification.objects.filter().delete()
    # print('delete_all usufructs...')
    # for usu in Usufruct.objects.filter():
    #     usu.delete()
    # print('delete_all activities...')
    # for act in Activity.objects.filter():
    #     act.delete()
    # print('delete_all acquisition periods...')
    # for acq in AcquisitionPeriod.objects.filter():
    #     acq.delete()
    # GroupPeriod.objects.filter().delete()
    # Configuration.objects.filter().delete()
    # print('delete_all end.')


def delete_employee(registry):
    user = get_current_user()
    set_current_user("athenas")
    BaseLicencaAfastamento.atualizar_estado = lambda x: True
    ServidorLotacao.call_update_from_departure = lambda x: True
    for usu in Usufruct.objects.filter(
        activity__acquisition_period__employee__matricula=registry
    ):
        usu.delete()
    for act in Activity.objects.filter(
        acquisition_period__employee__matricula=registry
    ):
        act.delete()
    for acq in AcquisitionPeriod.objects.filter(employee__matricula=registry):
        acq.delete()
    set_current_user(user)


def setUpModule():
    delete_all()
    # global scheduled
    # global finished
    # global active
    # scheduled = BaseLicencaAfastamento.objects.filter(servidor__matricula=79107, estado=SCHEDULED).values('pk')
    # finished = BaseLicencaAfastamento.objects.filter(servidor__matricula=79107, estado=FINISHED).values('pk')
    # active = BaseLicencaAfastamento.objects.filter(servidor__matricula=79107, estado=ACTIVE).values('pk')
    # BaseLicencaAfastamento.objects.filter(servidor__matricula=79107).update(estado=CANCELED)
    setUpModuleVacation()
    pass


scheduled = []
finished = []
active = []


def setUpModuleVacation():
    set_current_user("iradianmorais")
    mixer.blend(
        Attachment, created_by=get_current_user(), publication=Publicacao.objects.last()
    )
    BaseLicencaAfastamento.objects.filter(
        created_at__gte=datetime.datetime.now().date()
    ).update(alteracao=CANCELED, estado=CANCELED)

    configuration = Configuration.objects.filter(type_of_usufruct=CONF_VACATION)
    if not configuration.exists():
        configuration = mixer.blend(
            Configuration,
            created_by=get_current_user(),
            modified_by=get_current_user(),
            title="FÉRIAS SERVIDORES",
            type_of_usufruct=CONF_VACATION,
            authorizer_employee=Servidor.objects.get(matricula=75207),
            authorizer_member=Servidor.objects.get(matricula=4191),
            block_on_conflict=True,
            auto_create_on_scale=True,
            months_prescription=36,
            auto_create_prescription=True,
            min_days_sale=10,
            max_days_sale=20,
            months_exercise_first_acquitition=12,
            months_exercise_next_acquitition=12,
            auto_authorization=1,
            auto_homologation=AUTO_HOMOLOGATION,
            max_division=2,
            max_division_admin=2,
            min_days_division=10,
            min_days_division_admin=10,
            chronological_fruition=False,
            months_max_usufruct=None,
            max_alteration_usufruct=1,
            start_month_next_period=None,
            days_precede_fruition=None,
            work_days_precede_fruition=False,
            months_exercise_sale=None,
            days_per_period=30,
            periods_per_year=1,
            division_after_suspension=1,
        )
    else:
        configuration = configuration.first()
        Configuration.objects.filter(pk=configuration.pk).update(
            authorizer_employee=Servidor.objects.get(matricula=75207),
            authorizer_member=Servidor.objects.get(matricula=4191),
            block_on_conflict=True,
            auto_create_on_scale=True,
            months_prescription=36,
            auto_create_prescription=True,
            min_days_sale=10,
            max_days_sale=20,
            months_exercise_first_acquitition=12,
            months_exercise_next_acquitition=12,
            auto_authorization=1,
            auto_homologation=AUTO_HOMOLOGATION,
            max_division=2,
            max_division_admin=2,
            min_days_division=10,
            min_days_division_admin=10,
            chronological_fruition=False,
            months_max_usufruct=None,
            max_alteration_usufruct=1,
            start_month_next_period=None,
            days_precede_fruition=None,
            work_days_precede_fruition=False,
            months_exercise_sale=None,
            days_per_period=30,
            periods_per_year=1,
            division_after_suspension=1,
        )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.block_usufruct_departures.add(choice)

    group = GroupPeriod.objects.filter(
        configuration__type_of_usufruct=CONF_VACATION,
        year_reference=year_reference_vacation,
    )
    if not group.exists():
        group = mixer.blend(
            GroupPeriod,
            created_by=get_current_user(),
            modified_by=get_current_user(),
            configuration=configuration,
            title="FÉRIAS SERVIDORES",
            period=1,
            start_date_book=start_date_book,
            homologation_date=end_date_book,
            end_date_book=None,
            year_reference=year_reference_vacation,
        )
    else:
        group = group.first()

    acquisition_period = factory_acquisition_period(
        group, Servidor.objects.get(matricula=79107)
    )

    acquisition_period_68507 = factory_acquisition_period(
        group, Servidor.objects.get(matricula=68507)
    )
    acquisition_period_67807 = factory_acquisition_period(
        group, Servidor.objects.get(matricula=67807)
    )
    acquisition_period_6791 = factory_acquisition_period(
        group, Servidor.objects.get(matricula=6791)
    )

    AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(
        status=ACQP_PROGRESS
    )
    AcquisitionPeriod.objects.filter(pk=acquisition_period_68507.pk).update(
        status=ACQP_PROGRESS
    )
    AcquisitionPeriod.objects.filter(pk=acquisition_period_67807.pk).update(
        status=ACQP_PROGRESS
    )
    AcquisitionPeriod.objects.filter(pk=acquisition_period_6791.pk).update(
        status=ACQP_PROGRESS
    )

    group = GroupPeriod.objects.filter(
        configuration__type_of_usufruct=CONF_VACATION,
        year_reference=year_reference_vacation_begin,
    )
    if not group.exists():
        group = mixer.blend(
            GroupPeriod,
            created_by=get_current_user(),
            modified_by=get_current_user(),
            configuration=configuration,
            title="FÉRIAS SERVIDORES",
            period=1,
            start_date_book=start_date_book,
            end_date_book=end_date_book,
            year_reference=year_reference_vacation_begin,
        )
    else:
        group = group.last()
    acquisition_period = AcquisitionPeriod.objects.filter(
        group_period=group, employee__matricula=79107
    )
    if not acquisition_period.exists():
        acquisition_period = mixer.blend(
            AcquisitionPeriod,
            created_by=get_current_user(),
            modified_by=get_current_user(),
            group_period=group,
            employee=Servidor.objects.get(matricula=79107),
            status=ACQP_PROGRESS,
            start_date_acquisition=start_date_acquisition - relativedelta(years=1),
            end_date_acquisition=start_date_acquisition,
            start_date_fruition=start_date_fruition,
            end_date_fruition=None,
            continuous_period=True,
            blocked=False,
            days=30,
            paid_days_cache=0,
            paid_without_payroll=False,
            indemnified=False,
            suspended_days=0,
            period=1,
        )
    else:
        acquisition_period = acquisition_period.first()
    for usu in acquisition_period.usufructs:
        usu.delete()
    acquisition_period.activities.filter().delete()
    AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(
        status=ACQP_PROGRESS
    )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        acquisition_period.configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        acquisition_period.configuration.block_usufruct_departures.add(choice)


def setUpModuleRecess():
    mixer.blend(Attachment, publication=Publicacao.objects.last())
    BaseLicencaAfastamento.objects.filter(
        created_at__gte=datetime.datetime.now().date()
    ).update(alteracao=CANCELED, estado=CANCELED)
    for usu in Usufruct.objects.filter(
        activity__acquisition_period__employee__matricula=79107
    ):
        usu.delete()

    if VERBOSE:
        print("===============>setUpModule<========================")
    Notification.objects.filter().delete()
    group = generate_group_and_conf_recess()
    configuration = group.configuration
    acquisition_period = AcquisitionPeriod.objects.filter(
        group_period=group, employee__matricula=79107
    )
    if not acquisition_period.exists():
        acquisition_period = mixer.blend(
            AcquisitionPeriod,
            created_by=get_current_user(),
            modified_by=get_current_user(),
            group_period=group,
            employee=Servidor.objects.get(matricula=79107),
            status=ACQP_PROGRESS,
            start_date_acquisition=group.start_date_fruition,
            end_date_acquisition=group.end_date_fruition,
            start_date_fruition=group.start_date_fruition,
            end_date_fruition=group.end_date_fruition,
            continuous_period=True,
            blocked=False,
            days=configuration.days_per_period,
            period=1,
        )
    else:
        acquisition_period = acquisition_period.first()
    for usu in acquisition_period.usufructs:
        usu.delete()
    acquisition_period.activities.filter().delete()
    AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(
        status=ACQP_PROGRESS
    )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        acquisition_period.configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        acquisition_period.configuration.block_usufruct_departures.add(choice)


def tearDownModule():
    pass
    # global scheduled
    # global finished
    # global active
    # BaseLicencaAfastamento.objects.filter(servidor__matricula=79107, pk__in=scheduled).update(estado=SCHEDULED)
    # BaseLicencaAfastamento.objects.filter(servidor__matricula=79107, pk__in=finished).update(estado=FINISHED)
    # BaseLicencaAfastamento.objects.filter(servidor__matricula=79107, pk__in=active).update(estado=ACTIVE)


def factory_acquisition_period(group, employee):
    delete_employee(employee.matricula)
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "status": ACQP_PROGRESS,
        "start_date_acquisition": start_date_acquisition,
        "end_date_acquisition": end_date_acquisition,
        "start_date_fruition": start_date_fruition,
        "end_date_fruition": end_date_fruition,
        "continuous_period": True,
        "blocked": False,
        "days": 30,
        "paid_without_payroll": False,
        "indemnified": False,
    }
    acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
        group_period=group, employee=employee, defaults=defaults
    )
    for usu in acquisition_period.usufructs.filter():
        usu.delete()
    acquisition_period.activities.filter().delete()
    return acquisition_period


class GroupPeriodTestCase(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.skip("skipping test_run_generate_all_acquisition_periods_birthday_break")
    def test_run_generate_all_acquisition_periods_birthday_break(self):
        def get_acquisition_period_query(self):
            return Servidor.objects.filter(ativo=True).filter(matricula=94109)

        from rh.dayoff.classcodes.birthdaybreak import BirthdayBreak

        BirthdayBreak.get_acquisition_period_query = get_acquisition_period_query

        year = datetime.datetime.now().year
        group_period = generate_group_and_conf_birthday_break(year=year)
        group_period.run_generate_all_acquisition_periods(None, None)

    @unittest.skip("skipping test_run_generate_all_acquisition_periods_recess")
    def test_run_generate_all_acquisition_periods_recess(self):
        year = datetime.datetime.now().year
        group_period = generate_group_and_conf_recess(year=year)
        group_period.run_generate_all_acquisition_periods(None, None)

    # @unittest.skip('skipping test_acquisition_update') # 1
    def test_acquisition_update(self):
        print("test_acquisition_updatetest_acquisition_updatetest_acquisition_update")
        from rh.dayoff.classcodes.recess import Recess
        from rh.dayoff.classcodes.birthdaybreak import BirthdayBreak

        def get_acquisition_period_query(self):
            return Servidor.objects.filter(matricula=120513)

        # group_period = generate_group_and_conf_birthday_break(year=2020)
        BirthdayBreak.get_acquisition_period_query = get_acquisition_period_query
        group_period = GroupPeriod.objects.filter(
            year_reference=2020, configuration__type_of_usufruct=CONF_BIRTHDAY_BREAK
        ).last()
        print(f"group_period {group_period}")
        group_period.get_acquisition_period_query = get_acquisition_period_query
        print("test_acquisition_updatetest_acquisition_updatetest_acquisition_update")
        group_period.run_generate_all_acquisition_periods(None, None)

    @unittest.skip("skipping test_acquisition")
    def test_acquisition(self):

        def get_acquisition_period_query(self):
            types = [
                v["cvalue"]
                for v in self.group_period.configuration.type_employees.values("cvalue")
            ]
            return Servidor.objects.filter(
                ativo=True, type_by_possession__in=types
            ).filter(matricula__in=[14693, 120031])

        from rh.dayoff.classcodes.recess import Recess
        from rh.dayoff.classcodes.birthdaybreak import BirthdayBreak

        Recess.get_acquisition_period_query = get_acquisition_period_query
        BirthdayBreak.get_acquisition_period_query = get_acquisition_period_query

        registry = 14693
        year = datetime.datetime.now().year - 1
        group_period = generate_group_and_conf_birthday_break(year=year)
        group_period.run_generate_all_acquisition_periods(None, None)

        group_period = generate_group_and_conf_recess(year=year)
        group_period.run_generate_all_acquisition_periods(None, None)

        departure = (
            AfastamentoOutroOrgao.objects.filter(servidor__matricula=registry)
            .exclude(estado__in=[CANCELED, SCHEDULED, FINISHED])
            .last()
        )
        pr, created = Prorrogacao.objects.get_or_create(
            data_inicio=datetime.datetime(departure.data_fim.year + 1, 1, 1).date(),
            data_fim=datetime.datetime(year + 2, 12, 31).date(),
        )
        departure.prorrogacao.add(pr)
        departure.refresh_from_db()
        group_period = generate_group_and_conf_birthday_break(year=year + 1)
        group_period.run_generate_all_acquisition_periods(None, None)
        departure.prorrogacao.remove(pr)
        departure.save()

        group_period = generate_group_and_conf_recess(year=year + 1)
        group_period.run_generate_all_acquisition_periods(None, None)

        acquisition_period = factory_acquisition_period(
            group_period, Servidor.objects.get(matricula=115312)
        )
        AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(
            days=1, days_to_enjoy_cache=1, days_not_booked_cache=1
        )
        AcquisitionPeriod.acquisition_manager(Servidor.objects.get(matricula=115312))

        acquisition_period = factory_acquisition_period(
            group_period, Servidor.objects.get(matricula=120031)
        )
        print(f"group_period: {group_period} acquisition_period: {acquisition_period}")
        AcquisitionPeriod.acquisition_manager(Servidor.objects.get(matricula=120031))


class AcquisitionPeriodTestCase(unittest.TestCase):

    def setUp(self):
        self._acquisition_period = AcquisitionPeriod.objects.filter(
            group__configuration__type_of_usufruct=CONF_VACATION,
            group__year_reference=year_reference_vacation,
        ).first()

    @property
    def acquisition_period(self):
        self._acquisition_period.refresh_from_db()
        return self._acquisition_period

    # @unittest.skip('skiping test')
    def test(self):
        pass

    @unittest.skip("skiping test")
    def test_validate_continuous_period(self):
        assert self.acquisition_period.validate_continuous_period()

    @unittest.skip("skiping test")
    def test_validate_block_on_conflict(self):
        assert self.acquisition_period.validate_block_on_conflict()

    @unittest.skip("skiping test")
    def test_validate_block_after_pay(self):
        assert self.acquisition_period.validate_block_after_pay()

    @unittest.skip("skiping test")
    def test_validate_months_prescription(self):
        assert self.acquisition_period.validate_months_prescription()

    @unittest.skip("skiping test")
    def test_validate_min_days_division(self):
        assert self.acquisition_period.validate_min_days_division()

    @unittest.skip("skiping test")
    def test_validate_chronological_fruition(self):
        assert self.acquisition_period.validate_chronological_fruition()

    @unittest.skip("skiping test")
    def test_validate_days_precede_fruition(self):
        assert self.acquisition_period.validate_days_precede_fruition()

    @unittest.skip("skiping test")
    def test_validate_start_date_book(self):
        assert self.acquisition_period.validate_start_date_book()

    @unittest.skip("skiping test")
    def test_validate_end_date_book(self):
        assert self.acquisition_period.validate_end_date_book()

    @unittest.skip("skiping test")
    def test_validate_sale(self):
        assert self.acquisition_period.validate_sale()

    @unittest.skip("skiping test")
    def test_validate_months_exercise_sale(self):
        assert self.acquisition_period.validate_months_exercise_sale()

    @unittest.skip("skiping test")
    def test_validate_min_days_sale(self):
        assert self.acquisition_period.validate_min_days_sale()

    @unittest.skip("skiping test")
    def test_validate_max_days_sale(self):
        assert self.acquisition_period.validate_max_days_sale()

    @unittest.skip("skiping test")
    def test_validate_months_exercise_first_acquitition(self):
        assert self.acquisition_period.validate_months_exercise_first_acquitition()

    @unittest.skip("skiping test")
    def test_validate_months_exercise_next_acquitition(self):
        assert self.acquisition_period.validate_months_exercise_next_acquitition()

    @unittest.skip("skiping test")
    def test_validate_days_per_period(self):
        assert self.acquisition_period.validate_days_per_period()

    @unittest.skip("skiping test")
    def test_validate_periods_per_year(self):
        assert self.acquisition_period.validate_periods_per_year()

    @unittest.skip("skiping test")
    def test_validate_division_after_suspension(self):
        assert self.acquisition_period.validate_division_after_suspension()

    @unittest.skip("skiping test")
    def test_validate_suspend_acquisition_departures(self):
        assert self.acquisition_period.validate_suspend_acquisition_departures()

    @unittest.skip("skiping test")
    def test_validate_suspend_usufruct_departures(self):
        assert self.acquisition_period.validate_suspend_usufruct_departures()

    @unittest.skip("skiping test")
    def test_validate_block_usufruct_departures(self):
        assert self.acquisition_period.validate_block_usufruct_departures()

    @unittest.skip("skiping test")
    def test_auto_authorization(self):
        global VERBOSE
        VERBOSE = False
        set_current_user("athenas")
        Configuration.objects.filter(type_of_usufruct=CONF_VACATION).update(
            auto_homologation=AUTO_HOMOLOGATION_NOT
        )
        ActivityTestCase().test_book()
        AcquisitionPeriod.auto_authorization()

        # Configuration.objects.filter(type_of_usufruct=CONF_VACATION).update(auto_homologation=AUTO_HOMOLOGATION)
        # ActivityTestCase().test_book()
        # AcquisitionPeriod.auto_authorization()


class UsufructTestCase(unittest.TestCase):

    def setUp(self):
        if not hasattr(self, "_group"):
            self._group = GroupPeriod.objects.get(
                configuration__type_of_usufruct=CONF_VACATION,
                year_reference=year_reference_vacation,
                period=1,
            )

        acquisition_period = factory_acquisition_period(
            self._group, Servidor.objects.get(matricula=79107)
        )
        acquisition_period_68507 = factory_acquisition_period(
            self._group, Servidor.objects.get(matricula=68507)
        )
        acquisition_period_67807 = factory_acquisition_period(
            self._group, Servidor.objects.get(matricula=67807)
        )
        acquisition_period_6791 = factory_acquisition_period(
            self._group, Servidor.objects.get(matricula=6791)
        )
        acquisition_period_87708 = factory_acquisition_period(
            self._group, Servidor.objects.get(matricula=87708)
        )

        if not hasattr(self, "_acquisition_period"):
            self._acquisition_period = AcquisitionPeriod.objects.filter(
                employee__matricula=68507,
                group_period__configuration__type_of_usufruct=CONF_VACATION,
                group_period__year_reference=year_reference_vacation,
            ).first()

    @property
    def acquisition_period(self):
        self._acquisition_period.refresh_from_db()
        return self._acquisition_period

    def _book(
        self,
        usufructs=[],
        immediate_authorization=None,
        mediate_authorization=None,
        acquisition_period=None,
        context="employee",
    ):
        # print('_book____________________')
        if len(usufructs) == 0:
            today = datetime.datetime.now().date()
            start1 = today + relativedelta(days=56)
            start2 = today + relativedelta(days=76)
            usufructs = [
                {"start_date": start1, "end_date": start1 + relativedelta(days=9)},
                {"start_date": start2, "end_date": start2 + relativedelta(days=19)},
            ]
        acquisition_period = (
            self.acquisition_period if not acquisition_period else acquisition_period
        )
        acquisition_period.book(
            usufructs_in=usufructs,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )
        return len(usufructs)

    @unittest.skip("skiping test_conflicts_agreement")
    def test_conflicts_agreement(self):
        # setUpModuleVacation()
        set_current_user("robertasilva")
        today = datetime.datetime.now() + relativedelta(days=30)
        start1 = today + relativedelta(days=56)
        start2 = today + relativedelta(days=76)
        usufructs = [
            {"start_date": start1.date(), "end_date": start1 + relativedelta(days=9)},
            {"start_date": start2.date(), "end_date": start2 + relativedelta(days=19)},
        ]
        self._book(usufructs=usufructs)
        acquisition_period = AcquisitionPeriod.objects.filter(
            employee__matricula=67807,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation,
        ).first()
        set_current_user("josemarsilva")
        with self.assertRaises(Exception):
            self._book(acquisition_period=acquisition_period, usufructs=usufructs)

    @unittest.skip("skiping test_conflicts_move_substitution")
    def test_conflicts_move_substitution(self):
        # setUpModuleVacation()
        acquisition_period = AcquisitionPeriod.objects.filter(
            employee__matricula=6791,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation,
        ).first()
        set_current_user("marceloulisses")
        start_1 = datetime.datetime(year_reference_vacation, 12, 7).date()
        usufructs = [
            {"start_date": start_1, "end_date": start_1 + relativedelta(days=29)},
        ]
        # with self.assertRaises(Exception):
        self._book(acquisition_period=acquisition_period, usufructs=usufructs)

    @unittest.skip("skiping test_conflicts_substitutes")
    def test_conflicts_substitutes(self):
        # setUpModuleVacation()
        acquisition_period = AcquisitionPeriod.objects.filter(
            employee__matricula=79107,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation,
        ).first()
        set_current_user("brunnosilva")
        start_1 = datetime.datetime(2021, 2, 1).date()
        usufructs = [
            {"start_date": start_1, "end_date": start_1 + relativedelta(days=29)},
        ]
        self._book(acquisition_period=acquisition_period, usufructs=usufructs)

        acquisition_period = AcquisitionPeriod.objects.filter(
            employee__matricula=87708,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation,
        ).first()
        set_current_user("silviasoares")
        self._book(acquisition_period=acquisition_period, usufructs=usufructs)

    @unittest.skip("skiping test_conflicts_substitutes_member")
    def test_conflicts_substitutes_member(self):
        # setUpModuleVacation()
        acquisition_period = AcquisitionPeriod.objects.filter(
            employee__matricula=6791,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation,
        ).first()
        set_current_user("marceloulisses")
        print(f"\n\nUSER {get_current_user()}")
        start_1 = datetime.datetime(2020, 12, 7).date()
        usufructs = [
            {"start_date": start_1, "end_date": start_1 + relativedelta(days=29)},
        ]
        # with self.assertRaises(Exception):
        self._book(acquisition_period=acquisition_period, usufructs=usufructs)

        for employee in Servidor.objects.filter(tipo="M", ativo=True).filter(
            matricula__in=[6491]  # [82307, 32701]
        )[0:10]:
            acquisition_period = factory_acquisition_period(self._group, employee)
            print(f"\n\nUSER {employee}")
            set_current_user(employee.user)
            try:
                self._book(acquisition_period=acquisition_period, usufructs=usufructs)
            except Exception as err:
                print(err)

    # @unittest.skip('skiping test')
    # def test_validate_days_precede_fruition(self):
    #     assert self.usufruct.validate_days_precede_fruition()

    # @unittest.skip('skiping test')
    # def test_validate_work_days_precede_fruition(self):
    #     assert self.usufruct.validate_work_days_precede_fruition()


class ActivityTestCase(unittest.TestCase):

    def setUp(self):
        self._set_up()

    def _set_up(self):
        self._acquisition_period = AcquisitionPeriod.objects.filter(
            employee__matricula=79107,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation,
        ).first()

    @property
    def acquisition_period(self):
        self._set_up()
        # self._acquisition_period.refresh_from_db()
        return self._acquisition_period

    # @unittest.skip('skiping test_book') # 1
    def test_book(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        count = self._book()
        self._show_notification()
        self._show_annotation()
        assert self.acquisition_period.usufructs.filter(status=USU_NEW).count() == count

    # @unittest.skip('skiping test_book_admin_not_auto_authorization') # 1
    def test_book_admin_not_auto_authorization(self):
        pass
        # setUpModuleVacation()
        # Configuration.objects.filter(pk=self.acquisition_period.configuration.pk).update(auto_authorization=0)
        # set_current_user('iradianmorais')
        # count = self._book()
        # self._show_notification()
        # self._show_annotation()
        # Configuration.objects.filter(pk=self.acquisition_period.configuration.pk).update(auto_authorization=1)
        # assert self.acquisition_period.usufructs.filter(status=USU_NEW).count() == count

    # @unittest.skip('skiping test_book_admin') # 1
    def test_book_admin_authorize(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_authorization=1)
        set_current_user("iradianmorais")
        today = datetime.datetime.now()
        start_1 = today + relativedelta(days=30)
        start_2 = today + relativedelta(days=56)
        usufructs = [
            {"start_date": start_1, "end_date": start_1 + relativedelta(days=19)},
            {"start_date": start_2, "end_date": start_2 + relativedelta(days=9)},
        ]
        count = self._book(usufructs, context="admin")
        self._show_notification()
        self._show_annotation()
        assert (
            self.acquisition_period.usufructs.filter(activity__homologated=True).count()
            == count
        )

    # @unittest.skip('skiping test_book_admin') # 1
    def test_book_admin_immediate_mediate(self):
        setUpModuleVacation()
        set_current_user("iradianmorais")
        today = datetime.datetime.now()
        start1 = today + relativedelta(days=30)
        start2 = today + relativedelta(days=56)
        usufructs = [
            {"start_date": start1, "end_date": start1 + relativedelta(days=19)},
            {"start_date": start2, "end_date": start2 + relativedelta(days=9)},
        ]
        immediate = self.acquisition_period.employee.chefe_imediato
        mediate = immediate.chefe_imediato
        FeriasAfastamento.objects.filter(
            Q(servidor=self.acquisition_period.employee)
            & (
                (Q(data_inicio__lte=start1) & Q(data_fim__gte=start1))
                | (Q(data_inicio__lte=start2) & Q(data_fim__gte=start2))
            )
        ).exclude(estado=CANCELED).update(estado=CANCELED)
        count = self._book(
            usufructs,
            immediate_authorization=immediate,
            mediate_authorization=mediate,
            context="admin",
        )
        self._show_activities()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_authorization=1)
        assert (
            self.acquisition_period.usufructs.filter(activity__homologated=True).count()
            == count
        )

    # @unittest.skip('skiping test_book_admin') # 1
    def test_book_admin_auto_authorization_auto_homologation_not(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_authorization=1, auto_homologation=AUTO_HOMOLOGATION_NOT)
        set_current_user("iradianmorais")
        self._book(context="admin")
        self._show_notification()
        self._show_annotation()
        self._show_activities()
        assert self.acquisition_period.activities.last().status == ACT_ST_AUTHORIZED
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_authorization=1, auto_homologation=AUTO_HOMOLOGATION)

    # @unittest.skip('skiping test_book_admin') # 1
    def test_book_admin_auto_authorization_homologation(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_authorization=1, auto_homologation=AUTO_HOMOLOGATION)
        set_current_user("iradianmorais")
        count = self._book(context="admin")
        self._show_notification()
        self._show_annotation()
        self._show_activities()
        assert (
            self.acquisition_period.usufructs.filter(status=USU_HOMOLOGATED).count()
            == count
        )

    # @unittest.skip('skiping test_change_call') # 1
    def test_change_call(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")
        set_current_user("brunnosilva")
        self._change_call()
        self._show_notification()
        self._show_annotation()

    # @unittest.skip('skiping test_change') # 1
    def test_change(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")
        set_current_user("brunnosilva")
        self._change()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")

        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")
        set_current_user("brunnosilva")
        self._change()
        self._show_notification()
        self._show_annotation()

    # @unittest.skip('skiping test_change') # 1
    def test_change_all(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")

        set_current_user("brunnosilva")
        attachment = Attachment.objects.last()
        modifieds = []
        for usu in Usufruct.objects.filter(
            activity__in=self.acquisition_period.activities.values("pk"),
            status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI],
        ):
            if len(modifieds) == 0:
                modifieds.append(usu)
                start_date = usu.start_date + relativedelta(days=60)
                end_date = start_date + relativedelta(days=usu.days - 1)
                usufructs = [
                    {"start_date": start_date, "end_date": end_date},
                ]
        self.acquisition_period.change(
            usufructs_in=usufructs, modifieds=modifieds, attachment=attachment
        )
        set_current_user("sidneyjunior")
        self.acquisition_period.authorize_and_homologate(
            authorize=True, context="immediate"
        )

        # 2 PARA 1
        setUpModuleVacation()
        set_current_user("brunnosilva")
        today = datetime.datetime.now().date()
        usufructs = [
            {
                "start_date": today + relativedelta(days=36),
                "end_date": today + relativedelta(days=55),
            },
        ]
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")

        set_current_user("brunnosilva")
        attachment = Attachment.objects.last()
        modifieds = []
        days = 0
        for usu in Usufruct.objects.filter(
            activity__in=self.acquisition_period.activities.values("pk"),
            status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI],
        ):
            modifieds.append(usu)
            days += usu.days

        exclude = []
        for usu in self.acquisition_period.usufructs:
            for dep in self.acquisition_period.employee.departures_from_date(
                start_date=usu.start_date, end_date=usu.end_date
            ):
                exclude.append(dep.pk)
        FeriasAfastamento.objects.exclude(pk__in=exclude).update(
            alteracao=CANCELED, estado=CANCELED
        )

        start_date = usu.start_date + relativedelta(days=60)
        end_date = start_date + relativedelta(days=days - 1)
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]
        self.acquisition_period.change(
            usufructs_in=usufructs, modifieds=modifieds, attachment=attachment
        )
        set_current_user("sidneyjunior")
        self.acquisition_period.authorize_and_homologate(
            authorize=True, context="immediate"
        )

    # @unittest.skip('skiping test_change_admin') # 1
    def test_change_admin(self):
        setUpModuleVacation()
        set_current_user("iradianmorais")
        self._book(context="admin")
        self._change(context="admin")
        self._show_notification()
        self._show_annotation()

    # @unittest.skip('skiping test_interrupt') # 1
    def test_interrupt(self):
        setUpModuleVacation()
        set_current_user("iradianmorais")
        self._book(context="admin")
        self._interrupt()
        self._show_notification()
        self._show_annotation()

    # @unittest.skip('skiping test_suspend') # 1
    def test_suspend(self):
        setUpModuleVacation()
        set_current_user("iradianmorais")
        self._book(context="admin")
        self._suspend()
        self._show_notification()
        self._show_annotation()

    # @unittest.skip('skiping test_suspend_book') # 1
    def test_suspend_book(self):
        setUpModuleVacation()
        set_current_user("iradianmorais")
        self._book(context="admin")
        self._suspend_book()
        self._show_notification()
        self._show_annotation()

    # @unittest.skip('skiping test_cancel') # 1
    def test_cancel_admin(self):
        setUpModuleVacation()
        set_current_user("iradianmorais")
        self._book(context="admin")
        self._interrupt()
        with self.assertRaises(Exception):
            ActivityBook.objects.filter(
                acquisition_period=self.acquisition_period
            ).first().validate_cancel_last_activity()
        assert (
            ActivityInterrupt.objects.filter(acquisition_period=self.acquisition_period)
            .first()
            .validate_cancel_last_activity()
            is True
        )

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_authorization=1)
        set_current_user("iradianmorais")
        today = datetime.datetime.now().date()
        start_date1 = today + relativedelta(days=50)
        end_date1 = start_date1 + relativedelta(days=9)
        start_date2 = end_date1 + relativedelta(days=10)
        end_date2 = start_date2 + relativedelta(days=19)
        usufructs = [
            {"start_date": start_date1, "end_date": end_date1},
            {"start_date": start_date2, "end_date": end_date2},
        ]
        count = self._book(usufructs, context="admin")
        ActivityBook.objects.filter(
            acquisition_period=self.acquisition_period
        ).first().my_origin.cancel()
        self._show_notification()
        self._show_annotation()
        assert (
            self.acquisition_period.usufructs.filter(status=USU_CANCELED).count()
            == count
        )

    # @unittest.skip('skiping test_cancel') # 1
    def test_cancel(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        assert (
            ActivityBook.objects.filter(acquisition_period=self.acquisition_period)
            .first()
            .validate_cancel_last_activity()
            is True
        )

        setUpModuleVacation()
        set_current_user("iradianmorais")
        self._book(context="admin")
        self._interrupt()
        set_current_user("brunnosilva")
        with self.assertRaises(Exception):
            ActivityInterrupt.objects.filter(
                acquisition_period=self.acquisition_period
            ).first().validate_can_cancel()

        setUpModuleVacation()
        set_current_user("iradianmorais")
        self._book(context="admin")
        set_current_user("brunnosilva")
        with self.assertRaises(Exception):
            ActivityBook.objects.filter(
                acquisition_period=self.acquisition_period
            ).first().validate_can_cancel()

    # @unittest.skip('skiping test_release') # 1
    def test_release(self):
        setUpModuleVacation()
        ap = self._release()
        assert AcquisitionPeriod.objects.get(pk=ap.pk).status == ACQP_PROGRESS
        AcquisitionPeriod.objects.filter(pk=ap.pk).update(status=ACQP_PROGRESS)

    @unittest.skip("skiping test_homologate_batch")
    def test_homologate_batch(self):
        setUpModuleVacation()

        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION_NOT)
        set_current_user("brunnosilva")
        self._book()
        employee = employee_from_user(get_current_user())
        immediate = employee.chefe_imediato
        set_current_user(immediate.user)
        immediate.user.groups.add(Group.objects.get(name="dayoff-homologate"))
        immediate.user.refresh_from_db()
        self.acquisition_period.authorize(authorize=True, context="immediate")
        attachment = Attachment.objects.last()
        set_current_user("iradianmorais")
        AcquisitionPeriod.homologate_batch(
            group=self.acquisition_period.group_period.pk, attachment=attachment.pk
        )

        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION)

    # @unittest.skip('skiping test_book_annotation') # 1
    def test_book_annotation(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        self._show_annotation()

    # @unittest.skip('skiping test_interrupt_annotation') # 1
    def test_interrupt_annotation(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")
        self._interrupt()
        self._show_annotation()

    # @unittest.skip('skiping test_suspend_annotation') # 1
    def test_suspend_annotation(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")
        self._suspend()
        self._show_annotation()

    # @unittest.skip('skiping test_change_annotation') # 1
    def test_change_annotation(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")
        set_current_user("brunnosilva")
        self._change()
        self._show_annotation()

    @unittest.skip("skiping test_homologate_batch_annotation")
    def test_homologate_batch_annotation(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        immediate = employee_from_user(get_current_user()).chefe_imediato
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION_NOT)
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(
            immediate_authorization=immediate, context="admin"
        )
        self._show_activities()
        attachment = Attachment.objects.last()
        AcquisitionPeriod.homologate_batch(
            group=self.acquisition_period.group_period.pk, attachment=attachment.pk
        )
        time.sleep(10)
        self._show_annotation()
        self._show_activities()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION)

    @unittest.skip("skiping test_homologate_batch_activity")
    def test_homologate_batch_activity(self):
        # FIXME: CRIAÇÃO AUTOMÁTICA DE USUFRUTOS NÃO ESTÁ SENDO CHAMADA
        setUpModuleVacation()
        set_current_user("iradianmorais")
        group = generate_group_and_conf_recess()
        for usu in Usufruct.objects.filter(
            activity__acquisition_period__group_period=group
        ):
            usu.delete()
        for ap in group.acquisitionperiods.filter():
            for act in ap.activities.filter():
                act.delete()
            ap.delete()
        task = group.generate_acquisition_periods(create_or_update="create")
        state = task.state
        while state in ("initializing", "initialized", "progress"):
            state = Task.objects.get(uuid=task.uuid).state
            if VERBOSE:
                print("Criando períodos aquisitivos...%s" % state)
        attachment = Attachment.objects.last()
        activity = [
            act.pk
            for act in Activity.objects.filter(acquisition_period__group_period=group)
        ]
        task = AcquisitionPeriod.homologate_batch(
            activity=activity, attachment=attachment.pk
        )
        state = task.state
        while state in ("initializing", "initialized", "progress"):
            state = Task.objects.get(uuid=task.uuid).state
            if VERBOSE:
                print("Homologando atividades...%s" % state)
        if not Activity.objects.filter(pk__in=activity, homologated=False).exists():
            raise Exception("Nenhuma atividade de marcação para homologar.")
        assert (
            Activity.objects.filter(pk__in=activity, homologated=False).exists()
            is False
        )

    # @unittest.skip('skiping test_change_notify') # 1
    def test_change_notify(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(context="admin")
        self._change(context="admin")
        self._show_notification()

    # @unittest.skip('skiping test_authorize') # 1
    def test_authorize_admin(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize(context="admin")
        self._show_activities()
        assert (
            self.acquisition_period.activities.last().admin_authorization_by
            == get_current_user()
        )

    # @unittest.skip('skiping test_authorize') # 1
    def test_authorize_validate_usufrutcs(self):
        from rh.afastamento.models import FolgaEleitoral

        setUpModuleVacation()
        FolgaEleitoral.objects.filter(
            servidor=self.acquisition_period.employee
        ).delete()
        set_current_user("brunnosilva")
        self._book()
        set_current_user("iradianmorais")
        for usu in self.acquisition_period.usufructs.filter()[0:1]:
            departure = mixer.blend(
                "afastamento.FolgaEleitoral",
                servidor=usu.employee,
                ano=usu.start_date.year,
                data_inicio=usu.start_date,
                data_prevista=usu.end_date,
                data_fim=usu.end_date,
            )
        with self.assertRaises(Exception):
            usu.validate_departure()
        self.acquisition_period.configuration.block_usufruct_departures.remove(
            Choice.objects.get(
                app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO", value=38
            )
        )
        usu.validate_departure()
        BaseLicencaAfastamento.objects.filter(pk=departure.pk).update(estado=CANCELED)

    # @unittest.skip('skiping test_authorize') # 1
    def test_authorize_immediate_authorization(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        chief = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user(chief.user)
        self.acquisition_period.authorize(authorize=True, context="immediate")
        self._show_activities()
        assert (
            self.acquisition_period.activities.last().immediate_authorization_by
            == chief
        )

    # @unittest.skip('skiping test_authorize') # 1
    def test_authorize_immediate_authorization_wrong(self):
        setUpModuleVacation()
        set_current_user("brunnosilva")
        chief = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user(chief.chefe_imediato.user)
        with self.assertRaises(Exception):
            self.acquisition_period.authorize(authorize=True, context="immediate")

    # @unittest.skip('skiping test_authorize_mediate_authorization_not_required') # 1
    def test_authorize_mediate_authorization_not_required(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(mediate_authorization=False)
        set_current_user("brunnosilva")
        chief = employee_from_user(get_current_user()).chefe_imediato.chefe_imediato
        self._book()
        set_current_user(chief.user)
        with self.assertRaises(Exception):
            self.acquisition_period.authorize(authorize=True, context="mediate")

    # @unittest.skip('skiping test_authorize_mediate_authorization') # 1
    def test_authorize_mediate_authorization(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(mediate_authorization=True)
        set_current_user("brunnosilva")
        immediate = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user(immediate.user)
        self.acquisition_period.authorize(authorize=True, context="immediate")
        mediate = immediate.chefe_imediato
        mediate.user.groups.add(Group.objects.get(name="dayoff-mediate-chief"))
        set_current_user(mediate.user)
        self.acquisition_period.refresh_from_db()
        self.acquisition_period.authorize(authorize=True, context="mediate")
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert (
            activity.immediate_authorization_by == immediate
            and activity.mediate_authorization_by == mediate
        )

    # @unittest.skip('skiping test_authorize_admin_send_only_immediate_authorization') # 1
    def test_authorize_admin_send_only_immediate_authorization(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(mediate_authorization=False)
        set_current_user("brunnosilva")
        immediate = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(
            authorize=True, context="admin", immediate_authorization=immediate
        )
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert activity.immediate_authorization_by == immediate

    # @unittest.skip('skiping test_authorize_admin_send_immediate_authorization') # 1
    def test_authorize_admin_send_immediate_authorization(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(mediate_authorization=True)
        set_current_user("brunnosilva")
        immediate = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(
            authorize=True, context="admin", immediate_authorization=immediate
        )
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert activity.immediate_authorization_by == immediate

    # @unittest.skip('skiping test_authorize_admin_send_mediate_authorization') # 1
    def test_authorize_admin_send_mediate_authorization(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(mediate_authorization=True)
        set_current_user("brunnosilva")
        immediate = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(
            authorize=True,
            context="admin",
            immediate_authorization=immediate,
            mediate_authorization=immediate.chefe_imediato,
        )
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert (
            activity.immediate_authorization_by == immediate
            and activity.mediate_authorization_by == immediate.chefe_imediato
        )

    # @unittest.skip('skiping test_authorize_admin_send_mediate_immediate_authorization') # 1
    def test_authorize_admin_send_mediate_immediate_authorization(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(mediate_authorization=True)
        set_current_user("brunnosilva")
        immediate = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize_and_homologate(
            authorize=True,
            context="admin",
            immediate_authorization=immediate,
            mediate_authorization=immediate.chefe_imediato,
        )
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert (
            activity.immediate_authorization_by == immediate
            and activity.mediate_authorization_by == immediate.chefe_imediato
        )

    # @unittest.skip('skiping test_authorize_auto_homologation') # 1
    def test_authorize_auto_homologation(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION_NOT, mediate_authorization=False)
        set_current_user("brunnosilva")
        self._book()
        immediate = employee_from_user(get_current_user()).chefe_imediato
        set_current_user(immediate.user)
        self.acquisition_period.authorize(authorize=True, context="immediate")
        activity = self.acquisition_period.activities.last()
        assert activity.status == ACT_ST_AUTHORIZED

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION, mediate_authorization=False)
        set_current_user("brunnosilva")
        self._book()
        immediate = employee_from_user(get_current_user()).chefe_imediato
        set_current_user(immediate.user)
        self.acquisition_period.authorize(authorize=True, context="immediate")
        set_current_user(User.objects.last())
        with self.assertRaises(Exception):
            self.acquisition_period.homologate(context=True)

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION, mediate_authorization=False)
        set_current_user("brunnosilva")
        self._book()
        immediate = employee_from_user(get_current_user()).chefe_imediato
        set_current_user(immediate.user)
        self.acquisition_period.authorize(authorize=True, context="immediate")
        self.acquisition_period.homologate(context=True)
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert activity.homologation_by == immediate.user

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_homologation=AUTO_HOMOLOGATION, mediate_authorization=False)
        set_current_user("brunnosilva")
        immediate = employee_from_user(get_current_user()).chefe_imediato
        self._book()
        set_current_user("iradianmorais")
        self.acquisition_period.authorize(
            authorize=True, context="admin", immediate_authorization=immediate
        )
        self.acquisition_period.homologate(context=True)
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert activity.homologation_by == get_current_user()

    @unittest.skip("skiping test_validate_max_division")  # 1
    def test_validate_max_division(self):
        today = datetime.datetime.now().date()
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=1, max_division_admin=1)
        set_current_user("brunnosilva")
        """TESTA MARCAÇÃO DE 2 USUFRUTOS QUANDO MAX_DIVISION=1"""
        with self.assertRaises(Exception):
            self._book()

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=1, max_division_admin=1)
        set_current_user("brunnosilva")
        """TESTA MARCAÇÃO DE 1 com quantidade de dias menor USUFRUTOS QUANDO MAX_DIVISION=1"""
        usufructs = [
            {
                "start_date": today + relativedelta(days=36),
                "end_date": today + relativedelta(days=45),
            },
        ]
        with self.assertRaises(Exception):
            self._book(usufructs)

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=1, max_division_admin=2)
        set_current_user("iradianmorais")
        usufructs = [
            {
                "start_date": today + relativedelta(days=36),
                "end_date": today + relativedelta(days=45),
            },
        ]
        self._book(usufructs=usufructs, context="admin")

        set_current_user("brunnosilva")
        usufructs = [
            {
                "start_date": today + relativedelta(days=56),
                "end_date": today + relativedelta(days=75),
            }
        ]
        """TESTA MARCAÇÃO DE 2 USUFRUTOS QUANDO MAX_DIVISION=1, um feito por admin e o último por user"""
        self._book(usufructs=usufructs)

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)
        set_current_user("iradianmorais")
        self._book(context="admin")
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=1, max_division_admin=1)
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=75),
            },
            {
                "start_date": today + relativedelta(days=86),
                "end_date": today + relativedelta(days=105),
            },
        ]
        """TESTA ALTERAÇÃO PARA 2 USUFRUTOS QUANDO MAX_DIVISION=1"""
        with self.assertRaises(Exception):
            self._change(usufructs, context="admin")

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)
        set_current_user("iradianmorais")
        self._book(context="admin")
        # Configuration.objects.filter(pk=self.acquisition_period.configuration.pk).update(max_division=2, max_division_admin=2)
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=75),
            },
            {
                "start_date": today + relativedelta(days=86),
                "end_date": today + relativedelta(days=95),
            },
            {
                "start_date": today + relativedelta(days=106),
                "end_date": today + relativedelta(days=115),
            },
        ]
        """TESTA ALTERAÇÃO PARA 3 USUFRUTOS QUANDO MAX_DIVISION=2"""
        with self.assertRaises(Exception):
            self._change(usufructs, context="admin")

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)
        set_current_user("iradianmorais")
        usufructs = [
            {
                "start_date": today + relativedelta(days=36),
                "end_date": today + relativedelta(days=45),
            },
        ]
        self._book(usufructs=usufructs, context="admin")
        """TESTA MARCAÇÃO DE 3 com quantidade de dias não marcados USUFRUTOS QUANDO MAX_DIVISION=2"""
        with self.assertRaises(Exception):
            usufructs = [
                {
                    "start_date": today + relativedelta(days=66),
                    "end_date": today + relativedelta(days=75),
                },
                {
                    "start_date": today + relativedelta(days=86),
                    "end_date": today + relativedelta(days=95),
                },
                {
                    "start_date": today + relativedelta(days=106),
                    "end_date": today + relativedelta(days=115),
                },
            ]
            self._change(usufructs)
        """TESTA MARCAÇÃO DE 2 com quantidade de dias sobrando USUFRUTOS QUANDO MAX_DIVISION=2"""
        with self.assertRaises(Exception):
            usufructs = [
                {
                    "start_date": today + relativedelta(days=66),
                    "end_date": today + relativedelta(days=75),
                },
                {
                    "start_date": today + relativedelta(days=86),
                    "end_date": today + relativedelta(days=95),
                },
            ]
            self._change(usufructs)

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2, division_after_suspension=0)
        set_current_user("iradianmorais")
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=95),
            },
        ]
        self._book(usufructs=usufructs, context="admin")
        modifieds = []
        days_modified = 0
        days_interrupted = 21
        for usu in Usufruct.objects.filter(
            activity__in=self.acquisition_period.activities.values("pk"),
            status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI],
        )[0:1]:
            days_modified += usu.days
            modifieds.append(usu)
        start_date = usu.start_date
        end_date = start_date + relativedelta(days=days_modified - days_interrupted - 1)
        third = 11
        start_second = today + relativedelta(days=86)
        end_second = start_second + relativedelta(days=days_interrupted - 1 - third)
        start_third = today + relativedelta(days=106)
        end_third = start_third + relativedelta(days=third - 1)
        usufructs_in = [
            {"start_date": start_date, "end_date": end_date},
            {"start_date": start_second, "end_date": end_second},
            {"start_date": start_third, "end_date": end_third},
        ]
        """TESTA INTERRUPÇÃO PARA 3 USUFRUTOS QUANDO MAX_DIVISION=2, não deve validar"""
        self._interrupt(modifieds=modifieds, usufructs_in=usufructs_in)

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2, division_after_suspension=1)
        set_current_user("iradianmorais")
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=75),
            },
        ]
        self._book(usufructs=usufructs, context="admin")
        usufructs = [
            {
                "start_date": today + relativedelta(days=86),
                "end_date": today + relativedelta(days=102),
            }
        ]
        with self.assertRaises(Exception):
            self._book(usufructs=usufructs, context="admin")

        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)

    # @unittest.skip('skiping test_validate_booked_days') # 1
    def test_validate_booked_days(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)
        AcquisitionPeriod.objects.filter(pk=self.acquisition_period.pk).update(days=30)
        set_current_user("brunnosilva")
        """TESTA MARCAÇÃO ACQUISITIONPERIOD.DAYS +1 USUFRUTOS QUANDO MAX_DIVISION=2"""
        today = datetime.datetime.now()
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today
                + relativedelta(days=66 + self.acquisition_period.days),
            },
        ]
        with self.assertRaises(Exception):
            self._book(usufructs=usufructs)

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)
        AcquisitionPeriod.objects.filter(pk=self.acquisition_period.pk).update(days=30)
        days = self.acquisition_period.days / 2
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=66 + days),
            },
            {
                "start_date": today + relativedelta(days=106),
                "end_date": today + relativedelta(days=106 + days),
            },
        ]
        """TESTA MARCAÇÃO ACQUISITIONPERIOD.DAYS +2  USUFRUTOS QUANDO MAX_DIVISION=2"""
        with self.assertRaises(Exception):
            self._book(usufructs=usufructs)

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)
        AcquisitionPeriod.objects.filter(pk=self.acquisition_period.pk).update(days=30)
        days = self.acquisition_period.days / 2
        set_current_user("iradianmorais")
        self._book()
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=66 + days),
            },
            {
                "start_date": today + relativedelta(days=86),
                "end_date": today + relativedelta(days=86 + days),
            },
        ]
        """TESTA ALTERAÇÃO ACQUISITIONPERIOD.DAYS +2 (2 USUFRUCT)  USUFRUTOS QUANDO MAX_DIVISION=2"""
        with self.assertRaises(Exception):
            self._change(usufructs, context="admin")
        days = self.acquisition_period.days / 3
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=66 + days - 1),
            },
            {
                "start_date": today + relativedelta(days=86),
                "end_date": today + relativedelta(days=86 + days - 1),
            },
            {
                "start_date": today + relativedelta(days=106),
                "end_date": today + relativedelta(days=106 + days),
            },
        ]
        """TESTA ALTERAÇÃO ACQUISITIONPERIOD.DAYS +1 (3 USUFRUCT) USUFRUTOS QUANDO MAX_DIVISION=2"""
        with self.assertRaises(Exception):
            self._change(usufructs, context="admin")

        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(max_division=2, max_division_admin=2)
        AcquisitionPeriod.objects.filter(pk=self.acquisition_period.pk).update(days=30)
        set_current_user("iradianmorais")
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=95),
            },
        ]
        self._book(usufructs=usufructs, context="admin")
        modifieds = []
        days_modified = 0
        days_interrupted = 21
        for usu in Usufruct.objects.filter(
            activity__in=self.acquisition_period.activities.values("pk"),
            status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI],
        )[0:1]:
            days_modified += usu.days
            modifieds.append(usu)
        start_date = usu.start_date
        end_date = start_date + relativedelta(days=days_modified - days_interrupted - 1)
        today = datetime.datetime.now()
        start_second = today + relativedelta(days=86)
        end_second = start_second + relativedelta(days=days_interrupted)
        usufructs_in = [
            {"start_date": start_date, "end_date": end_date},
            {"start_date": start_second, "end_date": end_second},
        ]
        """TESTA INTERRUPÇÃO ACQUISITIONPERIOD.DAYS +1 PARA 2 USUFRUTOS QUANDO MAX_DIVISION=2"""
        with self.assertRaises(Exception):
            self._interrupt(modifieds=modifieds, usufructs_in=usufructs_in)

    # @unittest.skip('skiping test_authorize_auto_authorization') # 1
    def test_authorize_auto_authorization(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(auto_authorization=1)
        set_current_user("brunnosilva")
        self._book()
        self.acquisition_period.activities.filter().update(
            created_at=datetime.datetime(2020, 7, 29).date()
        )
        AcquisitionPeriod.auto_authorization()
        self._show_activities()
        activity = self.acquisition_period.activities.last()
        assert activity.admin_authorization_by == get_current_user()

    # @unittest.skip('skiping test_validate_chronological_fruition') # 1
    def test_validate_chronological_fruition(self):
        setUpModuleVacation()
        Configuration.objects.filter(type_of_usufruct=CONF_VACATION).update(
            auto_homologation=AUTO_HOMOLOGATION,
            auto_authorization=1,
            chronological_fruition=True,
        )
        acquisition_period = AcquisitionPeriod.objects.get(
            employee__matricula=79107,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation_begin,
        )
        set_current_user("iradianmorais")
        self._book(acquisition_period=acquisition_period)

        acquisition_period = AcquisitionPeriod.objects.get(
            employee__matricula=79107,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation,
        )
        today = datetime.datetime.now().date()
        usufructs = [
            {
                "start_date": today + relativedelta(days=16),
                "end_date": today + relativedelta(days=25),
            },
        ]
        with self.assertRaises(Exception):
            self._book(usufructs=usufructs, acquisition_period=acquisition_period)

        setUpModuleVacation()
        acquisition_period = AcquisitionPeriod.objects.get(
            employee__matricula=79107,
            group_period__configuration__type_of_usufruct=CONF_VACATION,
            group_period__year_reference=year_reference_vacation_begin,
        )
        Configuration.objects.filter(type_of_usufruct=CONF_VACATION).update(
            auto_homologation=AUTO_HOMOLOGATION,
            auto_authorization=1,
            chronological_fruition=True,
        )
        AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(
            booked_days_cache=20, real_days_cache=30
        )
        with self.assertRaises(Exception):
            self._book()

        Configuration.objects.filter(type_of_usufruct=CONF_VACATION).update(
            chronological_fruition=False
        )

    # @unittest.skip('skiping test_validate_min_days_division') # 1
    def test_validate_min_days_division(self):
        setUpModuleVacation()
        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(
            max_division=2,
            max_division_admin=2,
            min_days_division=10,
            min_days_division_admin=10,
        )
        today = datetime.datetime.now()
        set_current_user("brunnosilva")

        AcquisitionPeriod.objects.filter(pk=self.acquisition_period.pk).update(days=30)
        start_date = (today + relativedelta(days=66)).date()
        end_date = start_date + relativedelta(
            days=self.acquisition_period.configuration.min_days_division - 2
        )
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]
        """TESTA MARCAÇÃO MENOR QUE configuration.min_days_division"""
        with self.assertRaises(Exception):
            self._book(usufructs=usufructs)

        start_date = (today + relativedelta(days=66)).date()
        end_date = start_date + relativedelta(
            days=self.acquisition_period.configuration.min_days_division + 11
        )
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]
        """TESTA MARCAÇÃO QUE NÃO PERMITA OUTRA MARCAÇÃO SE ENCAIXE EM configuration.min_days_division"""
        with self.assertRaises(Exception):
            self._book(usufructs=usufructs)

        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(
            max_division=2,
            max_division_admin=2,
            min_days_division=2,
            min_days_division_admin=2,
        )
        start_date = (today + relativedelta(days=66)).date()
        end_date = start_date + relativedelta(
            days=self.acquisition_period.configuration.min_days_division - 2
        )
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]
        """TESTA MARCAÇÃO MENOR QUE configuration.min_days_division"""
        with self.assertRaises(Exception):
            self._book(usufructs=usufructs)

        Configuration.objects.filter(
            pk=self.acquisition_period.configuration.pk
        ).update(
            max_division=2,
            max_division_admin=2,
            min_days_division=10,
            min_days_division_admin=10,
        )

    @unittest.skip("skiping test_activity_status")
    def test_activity_status(self):
        set_current_user("athenas")
        ap = AcquisitionPeriod.objects.filter(
            employee__matricula=22999,
            group_period__configuration__type_of_usufruct=CONF_RECESS,
            group_period__year_reference=2020,
        ).first()
        AcquisitionPeriod.validate_can_delete = lambda x: True
        ap.usufructs.filter().delete()
        ap.activities.filter().delete()
        Recesso.objects.filter(
            estado__in=[CANCELED, ACTIVE, SCHEDULED, FINISHED], servidor=ap.employee
        ).delete()
        BaseLicencaAfastamento.objects.filter(
            estado__in=[
                ACTIVE,
            ],
            servidor__matricula=91108,
        ).update(estado=CANCELED)
        set_current_user("iradianmorais")
        # start_date = ap.start_date_fruition
        start_date = datetime.datetime.now().date() - relativedelta(days=2)
        # start_date = datetime.datetime.now().date() + relativedelta(days=5)
        end_date = start_date + relativedelta(days=17)
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]

        def _show(ap):
            print("_____show usufruct and departure")
            for usu in ap.usufructs.filter():
                print(
                    f"{usu} | {usu.departure.pk, usu.departure.__str_restful__() if usu.departure else None}"
                )
            # print('_____show activities')
            # for act in ap.activities.filter():
            #     print(f'{act}')

        print("=======>begin<===========")
        self._book(acquisition_period=ap, usufructs=usufructs, context="admin")
        _show(ap)

        usufruct = ap.usufructs.filter().last()
        MovimentacaoSubstituicao.objects.create(
            afastamento=usufruct.departure,
            posse=usufruct.employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="CM"
            ).last(),
            servidor_substituido=usufruct.employee,
            servidor=Servidor.objects.get(matricula=91108),  # agnel 46403
            data_inicio=usufruct.start_date,
            data_prevista=usufruct.end_date,
            data_fim=usufruct.end_date,
            designation_substituted=ServidorLotacao.objects.filter(
                servidor=usufruct.employee, ativo=True, lotacao__sigla="DMTI"
            ).last(),
        )

        # print('TEST INTERRUPT')
        # modifieds = []
        # for usu in Usufruct.objects.filter(
        #     activity__in=ap.activities.values('pk'), status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI, USU_ENJOYING, USU_ENJOYED]
        # )[0:1]:
        #     modifieds.append(usu)
        #     start_date = usu.start_date
        # # start_date = usu.start_date + relativedelta(days=10)
        # usufructs = [
        #     {'start_date': start_date, 'end_date': start_date + relativedelta(days=9)},
        # ]
        # self._interrupt(acquisition_period=ap, modifieds=modifieds, usufructs_in=usufructs)

        # print('TEST SUSPEND')
        # modifieds = []
        # for usu in Usufruct.objects.filter(
        #     activity__in=ap.activities.values('pk'), status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI, USU_ENJOYING, USU_ENJOYED]
        # )[0:1]:
        #     modifieds.append(usu)
        # self._suspend(acquisition_period=ap, modifieds=modifieds)

        # print('CANCEL SUSPENSION')
        # ap.activities.filter(canceled=False).latest('created_at').my_origin.cancel()

        # print('CANCEL INTERRUPTION')
        # ap.activities.filter(canceled=False).latest('created_at').my_origin.cancel()

    @unittest.skip("skiping test_suspend_usufruct_by_departure")
    def test_suspend_usufruct_by_departure(self):
        set_current_user("athenas")
        group = GroupPeriod.objects.filter(
            configuration__type_of_usufruct=CONF_VACATION,
            year_reference=year_reference_vacation,
        ).last()
        ap = factory_acquisition_period(group, Servidor.objects.get(matricula=22999))
        AcquisitionPeriod.validate_can_delete = lambda x: True

        for usu in ap.usufructs.filter():
            manager_usufruct(usu, to_delete=True)
            FeriasAfastamento.objects.filter(
                data_inicio=usu.start_date, servidor=ap.employee
            ).exlude(estado=CANCELED).update(estado=CANCELED, alteracao=CANCELED)
            for fa in FeriasAfastamento.objects.filter(
                data_inicio=usu.start_date, servidor=ap.employee
            ).exlude(estado=CANCELED):
                fa.save()

            LicencaSaudeJuntaMedica.objects.filter(
                servidor=ap.employee, data_inicio=usu.start_date - relativedelta(days=5)
            )
            for fa in LicencaSaudeJuntaMedica.objects.filter(
                data_inicio=usu.start_date - relativedelta(days=5), servidor=ap.employee
            ).exlude(estado=CANCELED):
                fa.save()

            usu.delete()
        ap.activities.filter().delete()

        set_current_user("iradianmorais")
        start_date = datetime.datetime.now().date() + relativedelta(days=5)
        end_date = start_date + relativedelta(days=17)
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]

        self._book(acquisition_period=ap, usufructs=usufructs, context="admin")

        usufruct = ap.usufructs.filter().last()

        set_current_user("iradianmorais")
        start_date = usufruct.start_date - relativedelta(days=5)
        end_date = start_date + relativedelta(days=14)
        lsj = LicencaSaudeJuntaMedica(
            servidor=usufruct.employee,
            data_inicio=start_date,
            data_prevista=end_date,
            data_fim=end_date,
            prazo_solicitado=15,
            prazo_concedido=15,
            aprovacao=DEFERIDA,
        )
        lsj.save()

    # @unittest.skip('skiping test_validate_substitution')
    def test_validate_substitution(self):
        set_current_user("athenas")
        group = GroupPeriod.objects.filter(
            configuration__type_of_usufruct=CONF_RECESS, year_reference=2020
        ).last()
        print(group)
        ap = factory_acquisition_period(group, Servidor.objects.get(matricula=22999))
        AcquisitionPeriod.objects.filter(pk=ap.pk).update(days=18)
        ap = AcquisitionPeriod.objects.get(pk=ap.pk)

        AcquisitionPeriod.validate_can_delete = lambda x: True
        ap.usufructs.filter().delete()
        ap.activities.filter().delete()
        MovimentacaoSubstituicao.objects.filter(
            afastamento__pk__in=BaseLicencaAfastamento.objects.filter(
                estado__in=[CANCELED, ACTIVE, SCHEDULED, FINISHED], servidor=ap.employee
            ).values("pk")
        ).delete()
        Recesso.objects.filter(
            estado__in=[CANCELED, ACTIVE, SCHEDULED, FINISHED], servidor=ap.employee
        ).update(estado=CANCELED)
        BaseLicencaAfastamento.objects.filter(
            estado__in=[
                ACTIVE,
            ],
            servidor__matricula=91108,
        ).update(estado=CANCELED)
        set_current_user("iradianmorais")
        # start_date = ap.start_date_fruition
        start_date = datetime.datetime.now().date() - relativedelta(days=2)
        # start_date = datetime.datetime.now().date() + relativedelta(days=5)
        end_date = start_date + relativedelta(days=17)
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]

        self._book(acquisition_period=ap, usufructs=usufructs, context="admin")

        usufruct = ap.usufructs.filter().last()

        MovimentacaoSubstituicao.objects.create(
            afastamento=usufruct.departure,
            posse=usufruct.employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="CM"
            ).last(),
            servidor_substituido=usufruct.employee,
            servidor=Servidor.objects.get(matricula=91108),  # agnel 46403
            data_inicio=usufruct.start_date,
            data_prevista=usufruct.end_date,
            data_fim=usufruct.end_date,
            designation_substituted=ServidorLotacao.objects.filter(
                servidor=usufruct.employee, ativo=True, lotacao__sigla="DMTI"
            ).last(),
        )

        group = GroupPeriod.objects.filter(
            configuration__type_of_usufruct=CONF_BIRTHDAY_BREAK, year_reference=2021
        ).last()
        ap = factory_acquisition_period(group, Servidor.objects.get(matricula=91108))
        AcquisitionPeriod.objects.filter(pk=ap.pk).update(days=1)
        ap = AcquisitionPeriod.objects.get(pk=ap.pk)
        AcquisitionPeriod.validate_can_delete = lambda x: True
        ap.usufructs.filter().delete()
        ap.activities.filter().delete()
        set_current_user("iradianmorais")
        # start_date = ap.start_date_fruition
        start_date = datetime.datetime.now().date() - relativedelta(days=2)
        # start_date = datetime.datetime.now().date() + relativedelta(days=5)
        end_date = start_date
        usufructs = [
            {"start_date": start_date, "end_date": end_date},
        ]

        with self.assertRaises(Exception):
            self._book(acquisition_period=ap, usufructs=usufructs, context="admin")

    def _book(
        self,
        usufructs=[],
        immediate_authorization=None,
        mediate_authorization=None,
        acquisition_period=None,
        context="employee",
    ):
        # print('_book____________________')
        acquisition_period = (
            self.acquisition_period if not acquisition_period else acquisition_period
        )
        if len(usufructs) == 0:
            today = datetime.datetime.now().date()
            usufructs = [
                {
                    "start_date": today + relativedelta(days=36),
                    "end_date": today + relativedelta(days=45),
                },
                {
                    "start_date": today + relativedelta(days=56),
                    "end_date": today + relativedelta(days=75),
                },
            ]
        acquisition_period.book(
            usufructs_in=usufructs,
            immediate_authorization=immediate_authorization,
            mediate_authorization=mediate_authorization,
            context=context,
        )
        return len(usufructs)

    def _change(self, usufructs=None, context="employee"):
        attachment = Attachment.objects.last()
        today = datetime.datetime.now().date()
        if not usufructs:
            usufructs = [
                {
                    "start_date": today + relativedelta(days=66),
                    "end_date": today + relativedelta(days=95),
                },
            ]
        modifieds = []
        for usu in Usufruct.objects.filter(
            activity__in=self.acquisition_period.activities.values("pk"),
            status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI],
        ):
            modifieds.append(usu)
        self.acquisition_period.change(
            usufructs_in=usufructs,
            modifieds=modifieds,
            attachment=attachment,
            context=context,
        )

    def _change_call(self, context="employee"):
        # CHANGE 1
        today = datetime.datetime.now().date()
        usufructs = [
            {
                "start_date": today + relativedelta(days=66),
                "end_date": today + relativedelta(days=75),
            },
            {
                "start_date": today + relativedelta(days=86),
                "end_date": today + relativedelta(days=105),
            },
        ]
        modifieds = []
        for usu in Usufruct.objects.filter(
            activity__in=self.acquisition_period.activities.values("pk"),
            status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI],
        ):
            modifieds.append(usu)
        self.acquisition_period.change(
            usufructs_in=usufructs, modifieds=modifieds, context=context
        )

    def _homologate(self):
        set_current_user("iradianmorais")
        self.acquisition_period.homologate()

    def _interrupt(self, modifieds=[], usufructs_in=[], acquisition_period=None):
        # print('_interrupt_________________')
        if not acquisition_period:
            acquisition_period = self.acquisition_period
        if not (modifieds or usufructs_in):
            modifieds = []
            for usu in Usufruct.objects.filter(
                activity__in=acquisition_period.activities.values("pk"),
                status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI, USU_ENJOYING],
            )[0:1]:
                modifieds.append(usu)
            start_date = usu.start_date
            usufructs_in = [
                {
                    "start_date": start_date,
                    "end_date": start_date + relativedelta(days=usu.days - 5),
                },
            ]
        acquisition_period.interrupt(usufructs_in=usufructs_in, modifieds=modifieds)

    def _suspend(self, modifieds=[], usufructs_in=[], acquisition_period=None):
        if not acquisition_period:
            acquisition_period = self.acquisition_period
        if not modifieds:
            modifieds = []
            for usu in Usufruct.objects.filter(
                activity__in=acquisition_period.activities.values("pk"),
                status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI, USU_ENJOYING],
            )[0:1]:
                modifieds.append(usu)
        acquisition_period.suspend(usufructs_in=usufructs_in, modifieds=modifieds)

    def _suspend_book(self):
        usufructs = []
        for usu in Usufruct.objects.filter(
            activity__in=self.acquisition_period.activities.values("pk"),
            status__in=[USU_HOMOLOGATED, USU_AUTORIZED_CI],
        )[0:1]:
            usufructs.append(usu)
            start_date = usu.start_date
        usufructs_in = [
            {
                "start_date": start_date,
                "end_date": start_date + relativedelta(days=usu.days - 5),
            },
        ]
        self.acquisition_period.suspend(usufructs_in=usufructs_in, modifieds=usufructs)
        # self.acquisition_period.authoriz)
        # self.acquisition_period.homologate()

    def _cancel(self):
        self.acquisition_period.my_origin.cancel()

    def _release(self):
        AcquisitionPeriod.objects.filter(pk=self.acquisition_period.pk).update(
            status=ACQP_WAIT
        )
        self.acquisition_period.refresh_from_db()
        self.acquisition_period.release()
        return self.acquisition_period

    def _show_notification(self):
        if VERBOSE:
            print("NOTIFICAÇÕES:")
            for n in Notification.objects.filter().order_by("created_at"):
                print(n.formatMsg())
                print("--------------------")

    def _show_annotation(self):
        if VERBOSE:
            print("ANOTAÇÕES:")
            for activity in self.acquisition_period.activities.filter().order_by(
                "created_at"
            ):
                print(
                    "%s -> %s"
                    % (
                        activity,
                        (
                            activity.annotation
                            if activity.annotation
                            else "NÃO EXISTE ANOTAÇÃO para esta ação"
                        ),
                    )
                )
                if activity.annotation:
                    print(activity.annotation.texto)
                print("--------------------")

    def _show_activities(self):
        if VERBOSE:
            print("AÇÕES:")
            for activity in self.acquisition_period.activities.filter().order_by(
                "created_at"
            ):
                print("%s" % (activity))
                print(
                    "immediate_authorization_by:  %s"
                    % (activity.immediate_authorization_by)
                )
                print(
                    "mediate_authorization_by:    %s"
                    % (activity.mediate_authorization_by)
                )
                print(
                    "admin_authorization_by:      %s"
                    % (activity.admin_authorization_by)
                )
                print("homologation_by:             %s" % (activity.homologation_by))
                print("=======================================")


def generate_group_and_conf_recess(year=None):
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "type_of_usufruct": CONF_RECESS,
        "class_code": ClassCode.objects.get(slug="dayoff-classcodes-recess"),
        "authorizer_employee": Servidor.objects.get(matricula=75207),
        "authorizer_member": Servidor.objects.get(matricula=4191),
        "block_on_conflict": True,
        "block_after_pay": False,
        "mediate_authorization": False,
        "auto_authorization": 1,
        "auto_create_on_scale": False,
        "months_prescription": None,
        "auto_create_prescription": False,
        "auto_homologation": AUTO_HOMOLOGATION_AFTER_SCALE,
        "max_division": 1,
        "max_division_admin": 1,
        "min_days_division": 1,
        "min_days_division_admin": 1,
        "chronological_fruition": False,
        "months_max_usufruct": None,
        "max_alteration_usufruct": None,
        "start_month_next_period": None,
        "days_precede_fruition": None,
        "work_days_precede_fruition": False,
        "months_exercise_sale": None,
        "min_days_sale": False,
        "max_days_sale": False,
        "months_exercise_first_acquitition": 0,
        "months_exercise_next_acquitition": None,
        "days_per_period": 50,
        "periods_per_year": 1,
        "division_after_suspension": 1,
    }
    configuration, created = Configuration.objects.get_or_create(
        title="RECESSO", type_of_usufruct=CONF_RECESS, defaults=defaults
    )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.block_usufruct_departures.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.suspend_acquisition_departures.add(choice)
    year = datetime.datetime.now().year if not year else year
    _year_next = (datetime.datetime.now() + relativedelta(years=1)).year
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "configuration": configuration,
        "year_reference": year,
        "end_date_book": None,
        "start_date_book": datetime.datetime.now().date(),
        "start_date_fruition": datetime.datetime(year, 12, 20).date(),
        "start_date_automatic_usufruct": datetime.datetime(year, 12, 20).date(),
        "end_date_automatic_usufruct": datetime.datetime(_year_next, 1, 6).date(),
    }
    group, created = GroupPeriod.objects.get_or_create(
        title="RECESSO", period=1, year_reference=year, defaults=defaults
    )
    return group


def generate_group_and_conf_birthday_break(year=None):
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "class_code": ClassCode.objects.get(slug="dayoff-classcodes-birthdaybreak"),
        "authorizer_employee": Servidor.objects.get(matricula=75207),
        "authorizer_member": Servidor.objects.get(matricula=4191),
        "block_on_conflict": True,
        "block_after_pay": False,
        "mediate_authorization": False,
        "auto_authorization": 1,
        "auto_create_on_scale": False,
        "months_prescription": 12,
        "auto_create_prescription": False,
        "auto_homologation": AUTO_HOMOLOGATION,
        "max_division": 1,
        "max_division_admin": 1,
        "min_days_division": 1,
        "min_days_division_admin": 1,
        "chronological_fruition": False,
        "months_max_usufruct": None,
        "max_alteration_usufruct": None,
        "start_month_next_period": None,
        "days_precede_fruition": None,
        "work_days_precede_fruition": False,
        "months_exercise_sale": None,
        "min_days_sale": False,
        "max_days_sale": False,
        "months_exercise_first_acquitition": 0,
        "months_exercise_next_acquitition": None,
        "days_per_period": 1,
        "periods_per_year": 1,
        "division_after_suspension": 1,
    }
    configuration, created = Configuration.objects.get_or_create(
        title="FOLGA ANIVERSÁRIO",
        type_of_usufruct=CONF_BIRTHDAY_BREAK,
        defaults=defaults,
    )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.block_usufruct_departures.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.suspend_acquisition_departures.add(choice)
    year = datetime.datetime.now().year if not year else year
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "configuration": configuration,
        "start_date_book": datetime.datetime(year, 1, 1).date(),
        "end_date_book": None,
        "start_date_fruition": datetime.datetime(year, 1, 1).date(),
        "end_date_fruition": None,
    }
    group, created = GroupPeriod.objects.get_or_create(
        title="FOLGA ANIVERSÁRIO", period=1, year_reference=year, defaults=defaults
    )
    return group


def generate_conf_electoral_slack():
    _year = datetime.datetime.now().year
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "authorizer_employee": Servidor.objects.get(matricula=75207),
        "authorizer_member": Servidor.objects.get(matricula=4191),
        "block_on_conflict": True,
        "block_after_pay": False,
        "mediate_authorization": False,
        "auto_authorization": 1,
        "auto_create_on_scale": False,
        "months_prescription": None,
        "auto_create_prescription": False,
        "auto_homologation": AUTO_HOMOLOGATION,
        "max_division": 1,
        "max_division_admin": 1,
        "min_days_division": 1,
        "min_days_division_admin": 1,
        "chronological_fruition": False,
        "months_max_usufruct": None,
        "max_alteration_usufruct": None,
        "start_month_next_period": None,
        "days_precede_fruition": None,
        "work_days_precede_fruition": False,
        "months_exercise_sale": None,
        "min_days_sale": False,
        "max_days_sale": False,
        "months_exercise_first_acquitition": 0,
        "months_exercise_next_acquitition": None,
        "days_per_period": None,
        "periods_per_year": 1,
        "division_after_suspension": 1,
    }
    configuration, created = Configuration.objects.get_or_create(
        title="Folga Eleitoral",
        type_of_usufruct=CONF_ELECTORAL_SLACK,
        defaults=defaults,
    )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.block_usufruct_departures.add(choice)
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "configuration": configuration,
        "start_date_book": datetime.datetime(_year, 12, 20).date(),
        "end_date_book": None,
        "start_date_fruition": datetime.datetime(_year, 12, 20).date(),
        "end_date_fruition": datetime.datetime(_year, 12, 20).date()
        + relativedelta(year=4),
    }
    group, created = GroupPeriod.objects.get_or_create(
        title="Folga de Eleitoral", period=1, year_reference=_year, defaults=defaults
    )
    return group


def generate_conf_dutty():
    _year = datetime.datetime.now().year
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "authorizer_employee": Servidor.objects.get(matricula=75207),
        "authorizer_member": Servidor.objects.get(matricula=4191),
        "block_on_conflict": True,
        "block_after_pay": False,
        "mediate_authorization": False,
        "auto_authorization": 1,
        "auto_create_on_scale": False,
        "months_prescription": None,
        "auto_create_prescription": False,
        "auto_homologation": AUTO_HOMOLOGATION,
        "max_division": 1,
        "min_days_division": 1,
        "min_days_division_admin": 1,
        "chronological_fruition": False,
        "months_max_usufruct": None,
        "max_alteration_usufruct": None,
        "start_month_next_period": None,
        "days_precede_fruition": None,
        "work_days_precede_fruition": False,
        "months_exercise_sale": None,
        "min_days_sale": False,
        "max_days_sale": False,
        "months_exercise_first_acquitition": 0,
        "months_exercise_next_acquitition": None,
        "days_per_period": None,
        "periods_per_year": 1,
        "division_after_suspension": 1,
    }
    configuration, created = Configuration.objects.get_or_create(
        title="Folga Plantão", type_of_usufruct=CONF_DUTTY, defaults=defaults
    )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.block_usufruct_departures.add(choice)
    group = mixer.blend(
        GroupPeriod,
        created_by=get_current_user(),
        modified_by=get_current_user(),
        configuration=configuration,
        start_date_book=datetime.datetime(_year, 12, 20).date(),
        end_date_book=None,
        start_date_fruition=datetime.datetime(_year, 12, 20).date(),
        end_date_fruition=datetime.datetime(_year, 12, 20).date()
        + relativedelta(year=4),
    )
    group, created = GroupPeriod.objects.get_or_create(
        title="Folga Plantão", period=1, year_reference=_year, defaults=defaults
    )
    return group


def generate_conf_compensation():
    _year = datetime.datetime.now().year
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "authorizer_employee": Servidor.objects.get(matricula=75207),
        "authorizer_member": Servidor.objects.get(matricula=4191),
        "block_on_conflict": True,
        "block_after_pay": False,
        "mediate_authorization": False,
        "auto_authorization": 1,
        "auto_create_on_scale": False,
        "months_prescription": None,
        "auto_create_prescription": False,
        "auto_homologation": AUTO_HOMOLOGATION,
        "max_division": 1,
        "min_days_division": 1,
        "min_days_division_admin": 1,
        "chronological_fruition": False,
        "months_max_usufruct": None,
        "max_alteration_usufruct": None,
        "start_month_next_period": None,
        "days_precede_fruition": None,
        "work_days_precede_fruition": False,
        "months_exercise_sale": None,
        "min_days_sale": False,
        "max_days_sale": False,
        "months_exercise_first_acquitition": 0,
        "months_exercise_next_acquitition": None,
        "days_per_period": None,
        "periods_per_year": 1,
        "division_after_suspension": 1,
    }
    configuration, created = Configuration.objects.get_or_create(
        title="Folga Compensação", type_of_usufruct=CONF_COMPENSATION, defaults=defaults
    )
    for choice in Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
    ):
        configuration.type_employees.add(choice)
    for choice in Choice.objects.filter(
        app_label="rh", name="TIPO_BASE_LICENCA_AFASTAMENTO"
    ):
        configuration.block_usufruct_departures.add(choice)
    defaults = {
        "created_by": get_current_user(),
        "modified_by": get_current_user(),
        "configuration": configuration,
        "start_date_book": datetime.datetime(_year, 12, 20).date(),
        "end_date_book": None,
        "start_date_fruition": datetime.datetime(_year, 12, 20).date(),
        "end_date_fruition": datetime.datetime(_year, 12, 20).date()
        + relativedelta(year=4),
    }
    group, created = GroupPeriod.objects.get_or_create(
        title="Folga Compensação", period=1, year_reference=_year, defaults=defaults
    )
    return group


def generate_configurations():
    generate_group_and_conf_recess()
    generate_group_and_conf_birthday_break()
    generate_conf_electoral_slack()
    generate_conf_dutty()
    generate_conf_compensation()


def create_acquisition_period(employees=[]):
    group = GroupPeriod.objects.filter(
        configuration__type_of_usufruct=CONF_VACATION
    ).first()
    for employee in Servidor.objects.filter(pk__in=employees):
        _create_acquisition_period(employee, group)


def _create_acquisition_period(employee, group):
    acquisition_period = mixer.blend(
        AcquisitionPeriod,
        created_by=get_current_user(),
        modified_by=get_current_user(),
        group_period=group,
        employee=employee,
        status=ACQP_PROGRESS,
        start_date_acquisition=start_date_acquisition,
        end_date_acquisition=end_date_acquisition,
        start_date_fruition=start_date_fruition,
        end_date_fruition=end_date_fruition,
        continuous_period=True,
        blocked=False,
        days=30,
        paid_days_cache=0,
        paid_without_payroll=False,
        indemnified=False,
        suspended_days=0,
        period=1,
    )
    print(acquisition_period)
    today = datetime.datetime.now().date()
    usufructs = [
        {
            "start_date": today + relativedelta(days=36),
            "end_date": today + relativedelta(days=45),
        },
        {
            "start_date": today + relativedelta(days=56),
            "end_date": today + relativedelta(days=75),
        },
    ]
    set_current_user(employee.user.username)
    acquisition_period.book(usufructs_in=usufructs)


def create_group_period_recess(year):
    defaults = {
        "class_code": ClassCode.objects.get(slug="dayoff-classcodes-recess"),
        "block_on_conflict": False,
        "block_after_pay": False,
        "mediate_authorization": False,
        "auto_authorization": 0,
        "auto_create_on_scale": False,
        "months_prescription": None,
        "auto_create_prescription": False,
        "auto_homologation": AUTO_HOMOLOGATION_AFTER_SCALE,
        "max_division": 1,
        "max_division_admin": 10,
        "min_days_division": 1,
        "min_days_division_admin": 1,
        "chronological_fruition": False,
        "months_max_usufruct": None,
        "max_alteration_usufruct": None,
        "start_month_next_period": None,
        "days_precede_fruition": None,
        "work_days_precede_fruition": False,
        "months_exercise_sale": None,
        "min_days_sale": False,
        "max_days_sale": False,
        "months_exercise_first_acquitition": 0,
        "months_exercise_next_acquitition": None,
        "days_per_period": 1000,
        "periods_per_year": 1,
        "division_after_suspension": 0,
    }
    configuration, created = Configuration.objects.get_or_create(
        title="RECESSO", type_of_usufruct=CONF_RECESS, defaults=defaults
    )
    start_date = datetime.datetime(int(year), 12, 20).date()
    defaults = {
        "configuration": configuration,
        "end_date_book": None,
        "start_date_book": start_date,
        "start_date_fruition": start_date,
        "homologation_date": start_date,
        "publication_date": start_date,
        "blocked": True,
    }
    group, created = GroupPeriod.objects.get_or_create(
        title="RECESSO", period=1, year_reference=year, defaults=defaults
    )
    return group


def run_create_acquisition_period_recess(departure):
    print(departure.__str_restful__())
    year_map = {
        "213/2014": 2013,
        "2007/2008": 2007,
        "2008/2009": 2008,
        "2009/2010": 2009,
        "2010/2011": 2010,
        "2011/2012": 2011,
        "2012/2013": 2012,
        "2013/2014": 2013,
        "2014/2015": 2014,
        "2015/2016": 2015,
        "2015/2015": 2015,
        "20162017": 2016,
        "20152018": 2018,
        "2011/2013": 2011,
    }
    year = year_map.get(departure.ano, departure.ano)
    group_period = create_group_period_recess(year)
    defaults = {
        "note": True,
        "status": ACQP_PROGRESS,
        "start_date_acquisition": group_period.start_date_fruition,
        "start_date_fruition": group_period.start_date_fruition,
        "continuous_period": True,
        "blocked": True,
        "days": group_period.configuration.days_per_period,
        "paid_days_cache": 0,
        "paid_without_payroll": False,
        "indemnified": False,
        "suspended_days": 0,
        "annotation": departure.anotacao_aquisicao,
    }
    acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
        group_period=group_period, employee=departure.servidor, defaults=defaults
    )
    print(created, acquisition_period)
    usufructs = [
        {"start_date": departure.data_inicio, "end_date": departure.data_fim},
    ]
    try:
        acquisition_period.book(usufructs_in=usufructs, context="admin")
    except Exception as err:
        print(err)
    return group_period


# from rh.dayoff.signals import departure as departure_signals

# def manager_departure(usufruct, cancel=None):
#     return True

# departure_signals.manager_departure = manager_departure

# def notify_release(self, notify_prevent=False):
#     return True

# def notify(self, notify_prevent=False):
#     return True

# def notify_authorize(self, notify_prevent=False):
#     return True

# def notify_homologated(self, notify_prevent=False):
#     return True

# def notify_fruition(cls, list_days=[]):
#     return True

# def notify(self, notify_prevent=False):
#     return True

# def notify_call_authorization(self, notify_prevent=False):
#     return True

# def notify(self, notify_prevent=False):
#     return True

# def notify_authorize(self, notify_prevent=False):
#     return True

# Activity.notify_release = notify_release
# Activity.notify = notify
# Activity.notify_authorize = notify_authorize
# Activity.notify_homologated = notify_homologated
# Activity.notify_fruition = notify_fruition
# Activity.notify = notify
# Activity.notify_call_authorization = notify_call_authorization
# Activity.notify = notify
# Activity.notify_authorize = notify_authorize

# ActivityBook.notify_release = notify_release
# ActivityBook.notify = notify
# ActivityBook.notify_authorize = notify_authorize
# ActivityBook.notify_homologated = notify_homologated
# ActivityBook.notify_fruition = notify_fruition
# ActivityBook.notify = notify
# ActivityBook.notify_call_authorization = notify_call_authorization
# ActivityBook.notify = notify
# ActivityBook.notify_authorize = notify_authorize


def call_create_acquisition_period_recess():
    # delete_all()
    set_current_user("iradianmorais")
    # for recess in Recesso.objects.filter().exclude(estado=CANCELED).order_by('ano'):
    #     info.update({recess.ano: (info.get(recess.ano, 0) + 1)})
    # for rs in info:
    #     print('RECESSO: %s' % rs, ' - COUNTER: %s' % info.get(rs))
    #     group = self._create_group_period(recess.ano)
    #     print(group)
    query = Recesso.objects.filter(servidor__tipo__in=["S", "M"]).exclude(
        estado=CANCELED
    )
    total = query.count()
    count = 0
    print("%s of %s" % (count, total))
    for recess in query.order_by("ano"):
        count += 1
        group_period = run_create_acquisition_period_recess(recess)
        print("%s of %s" % (count, total))

    # Configuration.objects.filter(pk=group_period.configuration.pk).update(days_per_period=10)


class MigrateRecessTestCase(unittest.TestCase):

    def test(self):
        call_create_acquisition_period_recess()


def create_group_period_electoral_break(year, period):
    from datetime import datetime

    if period == 3:
        period = 1
    defaults = {
        "block_on_conflict": False,
        "block_after_pay": False,
        "mediate_authorization": False,
        "auto_authorization": 0,
        "auto_create_on_scale": False,
        "months_prescription": None,
        "auto_create_prescription": False,
        "auto_homologation": AUTO_HOMOLOGATION_AFTER_SCALE,
        "max_division": 20,
        "max_division_admin": 20,
        "min_days_division": 1,
        "min_days_division_admin": 1,
        "chronological_fruition": False,
        "months_max_usufruct": None,
        "max_alteration_usufruct": None,
        "start_month_next_period": None,
        "days_precede_fruition": None,
        "work_days_precede_fruition": False,
        "months_exercise_sale": None,
        "min_days_sale": False,
        "max_days_sale": False,
        "months_exercise_first_acquitition": 0,
        "months_exercise_next_acquitition": None,
        "days_per_period": 1000,
        "periods_per_year": 1,
        "division_after_suspension": 0,
    }
    configuration, created = Configuration.objects.get_or_create(
        title="Folga Eleitoral",
        type_of_usufruct=CONF_ELECTORAL_SLACK,
        defaults=defaults,
    )
    start_date = datetime(int(year), 6, 1).date()
    defaults = {
        "configuration": configuration,
        "end_date_book": None,
        "start_date_book": start_date,
        "start_date_fruition": start_date,
        "homologation_date": start_date,
        "publication_date": start_date,
        "blocked": True,
    }
    group, created = GroupPeriod.objects.get_or_create(
        title="Folga Eleitoral", period=period, year_reference=year, defaults=defaults
    )
    return group


def run_create_acquisition_period_electoral_break(departure, user, success):
    # state = 'progress'
    # task = Task.objects.get(uuid=task)
    set_current_user(user)
    # departure = FolgaEleitoral.objects.get(pk=departure)
    group_period = create_group_period_electoral_break(departure.ano, departure.turno)
    defaults = {
        "note": True,
        "status": ACQP_PROGRESS,
        "start_date_acquisition": group_period.start_date_fruition,
        "start_date_fruition": group_period.start_date_fruition,
        "continuous_period": True,
        "blocked": True,
        "days": group_period.configuration.days_per_period,
        "paid_days_cache": 0,
        "paid_without_payroll": False,
        "indemnified": False,
        "suspended_days": 0,
        "annotation": departure.anotacao_aquisicao,
    }
    acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
        group_period=group_period, employee=departure.servidor, defaults=defaults
    )
    print(created, acquisition_period)
    usufructs = [
        {"start_date": departure.data_inicio, "end_date": departure.data_fim},
    ]
    try:
        acquisition_period.book(usufructs_in=usufructs, context="admin")
        # state = 'ready'
        # task.info(msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1)
        # message = 'Finalizando processamento.'
    except Exception as err:
        print(err)
    #     message = '%s' % err
    # task.message = message
    # task.finish_execution(status=state, msg=message)
    return group_period


def call_create_acquisition_period_electoral_slack():
    # from rh.dayoff.tasks import run_create_acquisition_period_electoral_break
    # delete_all()
    set_current_user("iradianmorais")
    FolgaEleitoral.objects.filter(ano=210).update(ano=2010)
    info = {}
    for departure in (
        FolgaEleitoral.objects.filter(servidor__tipo__in=["S", "M"])
        .exclude(estado=CANCELED)
        .order_by("ano")
    ):
        info.update({departure.ano: (info.get(departure.ano, 0) + 1)})
    for rs in info:
        print("Folga Eleitoral: %s" % rs, " - COUNTER: %s" % info.get(rs))
        # group = self._create_group_period(departure.ano, departure.turno)
        # print(group)
    query = FolgaEleitoral.objects.filter(servidor__tipo__in=["S", "M"]).exclude(
        estado=CANCELED
    )
    total = query.count()
    count = 0
    print("%s of %s" % (count, total))
    for departure in query.order_by("ano", "data_inicio", "servidor"):
        # print(departure.ano, departure.__str_restful__())
        count += 1
        if departure.ano != 0:
            group_period = run_create_acquisition_period_electoral_break(
                departure, "iradianmorais", ""
            )

            # Task.start(
            #     run_create_acquisition_period_electoral_break,
            #     departure=departure.pk,
            #     user=get_current_user().username,
            #     success='''Período aquisitivo criado com sucesso %(acquisition_period)s.'''
            # )
        else:
            print(departure)
        print("%s of %s" % (count, total))
    # Configuration.objects.filter(pk=group_period.configuration.pk).update(days_per_period=10)


class MigrateElectoralSlackTestCase(unittest.TestCase):

    def test(self):
        call_create_acquisition_period_electoral_slack()


class MigrateTestCase(unittest.TestCase):

    def test(self):
        # delete_all()
        call_create_acquisition_period_recess()
        call_create_acquisition_period_electoral_slack()

        count = 0
        query = AcquisitionPeriod.objects.filter()
        total = query.count()
        for ap in query:
            booked_days = ap.booked_days
            print(
                f"{ap}\nbooked_days_cache: {ap.booked_days_cache} booked_days: {booked_days}"
            )
            AcquisitionPeriod.objects.filter(pk=ap.pk).update(days=booked_days)
            AcquisitionPeriod.objects.get(pk=ap.pk).save()
            count += 1
            print(f"{count} of {total}")

        # for ap in AcquisitionPeriod.objects.filter():
        #     if ap.annotation:
        #         print(ap)
        #         print('resumo', ap.annotation.resumo)
        #         print('texto', ap.annotation.texto)
        #         print('==============================')

        def list_departure(ap):
            days = 0
            for dep in ap.configuration.departure_class.objects.filter(
                servidor=ap.employee, ano=ap.group_period.year_reference
            ).exclude(estado=CANCELED):
                days += NewDateRange(dep.data_inicio, dep.data_fim).days
                print(
                    "ano: %s" % dep.ano,
                    "|",
                    "chave: %s | " % dep.pk,
                    dep.__str_restful__(),
                    "| dias:",
                    NewDateRange(dep.data_inicio, dep.data_fim).days,
                )
            print("total dias dos afastamentos %s" % days)

        for ap in AcquisitionPeriod.objects.filter(
            booked_days_cache__gt=18, employee__ativo=True
        ).order_by("employee"):
            print(ap)
            list_departure(ap)
            print("===========================================")


"""
    PENDÊNCIAS:
        CORRIGIR ANO DE RECESSO
        CORRIGIR ANO DE FOLGA ELEITORAL com ano 0
        PARA FOLGA ELEITORAL EXISTE UMA QUESTÃO:
            EM 2018 HOUVE DUAS ELEIÇÕES E NÃO É POSSÍVEL SEPARAR OS PERÍODOS AQUISITIVOS, POR ISSO JUNTEI TODOS, TANTO DA ELEIÇÃO COMPLEMENTAR COMO A ELEIÇÃO GERAL
        ALGUMAS FOLGAS ELEITORAIS ESTÃO COM ANO DE FRUIÇÃO E NÃO O ANO DA ELEIÇÃO
"""
