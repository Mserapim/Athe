# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import Q, Count

from contrib.middleware import set_current_user, get_current_user
from contrib.daterange import NewDateRange
from rh.models import Servidor
from rh.const import CANCELED
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
from rh.dayoff.const import (
    ACQP_PROGRESS,
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
)
from rh.dayoff.signals import departure as departure_signals
from rh.afastamento.models import Recesso, FolgaEleitoral
from standard.models import ClassCode

from contrib.utils import getLogger


import datetime
import time


log = getLogger(__name__)


set_current_user("iradianmorais")


def manager_departure(usufruct, cancel=None):
    return True


departure_signals.manager_departure = manager_departure


def notify_release(self, notify_prevent=False):
    return True


def notify(self, notify_prevent=False):
    return True


def notify_authorize(self, notify_prevent=False):
    return True


def notify_homologated(self, notify_prevent=False):
    return True


def notify_fruition(cls, list_days=[]):
    return True


def notify(self, notify_prevent=False):
    return True


def notify_call_authorization(self, notify_prevent=False):
    return True


def notify(self, notify_prevent=False):
    return True


def notify_authorize(self, notify_prevent=False):
    return True


def validate_range_fruition(self):
    return True


def validate_days_per_period(self):
    return True


Activity.notify_release = notify_release
Activity.notify = notify
Activity.notify_authorize = notify_authorize
Activity.notify_homologated = notify_homologated
Activity.notify_fruition = notify_fruition
Activity.notify = notify
Activity.notify_call_authorization = notify_call_authorization
Activity.notify = notify
Activity.notify_authorize = notify_authorize

ActivityBook.notify_release = notify_release
ActivityBook.notify = notify
ActivityBook.notify_authorize = notify_authorize
ActivityBook.notify_homologated = notify_homologated
ActivityBook.notify_fruition = notify_fruition
ActivityBook.notify = notify
ActivityBook.notify_call_authorization = notify_call_authorization
ActivityBook.notify = notify
ActivityBook.notify_authorize = notify_authorize

Usufruct.validate_range_fruition = validate_range_fruition

AcquisitionPeriod.validate_days_per_period = validate_days_per_period


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
    log.debug(departure.__str_restful__())
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
    log.debug(f"{created}, {acquisition_period}")
    usufructs = [
        {"start_date": departure.data_inicio, "end_date": departure.data_fim},
    ]
    try:
        if acquisition_period.days != 1000:
            AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(days=1000)
            acquisition_period.refresh_from_db()
        acquisition_period.book(usufructs_in=usufructs, context="admin")
    except Exception as err:
        print(err)
    return group_period


def query_recess():
    return Recesso.objects.filter(servidor__tipo__in=["S", "M"]).exclude(
        estado=CANCELED
    )


def call_create_acquisition_period_recess():
    query = query_recess()
    total = query.count()
    count = 0
    # print(f'{count} of {total}'))
    log.debug(f"{count} of {total}")
    for recess in query.order_by("-ano"):
        count += 1
        group_period = run_create_acquisition_period_recess(recess)
        # print(f'{count} of {total}'))
        log.debug(f"{count} of {total}")


def migrate_recess():
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
        title="FOLGA ELEITORAL",
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


def run_create_acquisition_period_electoral_break(departure, success):
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
    log.debug(f"{created}, {acquisition_period}")
    usufructs = [
        {"start_date": departure.data_inicio, "end_date": departure.data_fim},
    ]
    try:
        if acquisition_period.days != 1000:
            AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(days=1000)
            acquisition_period.refresh_from_db()
        acquisition_period.book(usufructs_in=usufructs, context="admin")
    except Exception as err:
        print(err)
    return group_period


def query_electoral_slack():
    return FolgaEleitoral.objects.filter(servidor__tipo__in=["S", "M"]).exclude(
        estado=CANCELED
    )


def call_create_acquisition_period_electoral_slack():
    FolgaEleitoral.objects.filter(ano=210).update(ano=2010)
    query = query_electoral_slack()
    # info = {}
    # for departure in query.order_by('-ano'):
    #     info.update({departure.ano: (info.get(departure.ano, 0) + 1)})
    # for rs in info:
    #     print('Folga Eleitoral: %s' % rs, ' - COUNTER: %s' % info.get(rs))
    total = query.count()
    count = 0
    # print(f'{count} of {total}')
    log.debug(f"{count} of {total}")
    for departure in query.order_by("-ano", "data_inicio", "servidor"):
        count += 1
        if departure.ano != 0:
            group_period = run_create_acquisition_period_electoral_break(departure, "")
        else:
            print(departure)
        # print(f'{count} of {total}')
        log.debug(f"{count} of {total}")


def migrate_electoral():
    call_create_acquisition_period_electoral_slack()


def migrate_all():
    usufructs_before = Usufruct.objects.filter().count()

    call_create_acquisition_period_recess()
    call_create_acquisition_period_electoral_slack()

    count = 0
    query = AcquisitionPeriod.objects.filter()
    total = query.count()
    print("Atualizando Períodos aquisitivos...")
    log.debug("Atualizando Períodos aquisitivos...")
    for ap in query:
        booked_days = ap.booked_days
        if ap.days != ap.booked_days:
            # print(f'{ap}\nbooked_days_cache: {ap.booked_days_cache} booked_days: {booked_days}')
            log.debug(
                f"{ap}\nbooked_days_cache: {ap.booked_days_cache} booked_days: {booked_days}"
            )
            AcquisitionPeriod.objects.filter(pk=ap.pk).update(days=booked_days)
            AcquisitionPeriod.objects.get(pk=ap.pk).save()
            count += 1
            # print(f'{count} of {total}')
            log.debug(f"{count} of {total}")

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

    print(
        f"Usufrutos de afastamentos: {query_electoral_slack().count() + query_recess().count()}\n usufrutos do dayoff antes: {usufructs_before} \n usufrutos do dayoff depois: {Usufruct.objects.filter().count()}"
    )


migrate_all()
