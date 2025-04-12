# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.models import AcquisitionPeriod
from datetime import datetime
from rh.pvf.const import RESIDENTS_RECESS
from rh.dayoff.const import ACQP_PROGRESS
from rh.dayoff.models import ActivityBook
from contrib.daterange import NewDateRange


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """
        Este comando irá executar uma rotina diaria que cadastra o agendamento do usufruto do 
        proximo periodo aquisitivo para proximo recesso de residentes
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.resident_recess_period()

    def resident_recess_period(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando rotina de agendamento de recesso de residentes >>>>>>>>>>>>>"
        )
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando rotina de agendamento de recesso de residentes >>>>>>>>>>>>>"
        )

        for acq_period in AcquisitionPeriod.objects.filter(
            employee__exercise_date__isnull=False,
            employee__exercise_date__year__gte=2022,
            status=ACQP_PROGRESS,
            group_period__configuration__sub_type_of_usufruct__in=[RESIDENTS_RECESS],
        ):
            try:

                if acq_period.days_not_booked_cache > 0:
                    start_date = acq_period.group_period.start_date_automatic_usufruct
                    end_date = acq_period.group_period.end_date_automatic_usufruct
                    if (
                        start_date
                        and end_date
                        and (
                            not acq_period.employee.termination_date
                            or acq_period.employee.termination_date >= end_date
                        )
                    ):
                        book_usufructs = [
                            {
                                "days": NewDateRange(start_date, end_date).days,
                                "start_date": start_date,
                                "end_date": end_date,
                            }
                        ]
                        act_book = ActivityBook.do(
                            acquisition_period=acq_period,
                            usufructs_in=book_usufructs,
                            modifieds=[],
                            authorize=True,
                            attachment=None,
                            justification=None,
                            note=True,
                            immediate_authorization=None,
                            mediate_authorization=None,
                            context=None,
                            validate_prevent_usufruct=True,
                        )
                        log.info(f"Agendado: {act_book.employee} {act_book}")

            except Exception as err:
                log.info(err)
                print(err)

        log.info(
            ">>> [%s] Finalizando rotina de agendamento de recesso de residentes >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
        print(
            ">>> [%s] Finalizando rotina de agendamento de recesso de residentes >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
