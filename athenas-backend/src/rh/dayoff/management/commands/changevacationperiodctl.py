# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.models import AcquisitionPeriod, AcquisitionPeriodAttachment
from datetime import datetime
from dateutil.relativedelta import relativedelta
from rh.pvf.const import INDIVIDUAL_VACATION, REGULAR_VACATIONS


log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando irá alterar os períodos aquisitivos de férias  para nova regrar a partir de 2022
     - Executado uma única vez
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.change_vacation_period()

    def change_vacation_period(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando alteração das férias para nova regra 2022 >>>>>>>>>>>>>"
        )
        try:
            for acq_period in AcquisitionPeriod.objects.filter(
                end_date_acquisition__year__gt=2021,
                group_period__configuration__sub_type_of_usufruct__in=[
                    REGULAR_VACATIONS,
                    INDIVIDUAL_VACATION,
                ],
            ):
                if acq_period.employee.data_exercicio:
                    if acq_period.employee.data_exercicio.year < 2021:
                        acq_period.end_date_acquisition = datetime.strptime(
                            f"31/12/{acq_period.start_date_acquisition.year}",
                            "%d/%m/%Y",
                        ).date()
                        acq_period.description = (
                            acq_period.start_date_acquisition.strftime("%d/%m/%Y")
                            + " - "
                            + acq_period.end_date_acquisition.strftime("%d/%m/%Y")
                        )
                        acq_period.start_date_fruition = (
                            acq_period.end_date_acquisition + relativedelta(days=1)
                        )
                        acq_period.save()
                        attachment = AcquisitionPeriodAttachment.objects.filter(
                            acquisition_period=acq_period
                        ).first()
                        attachment.date_end = acq_period.end_date_acquisition
                        attachment.description = acq_period.description
                        attachment.save()

        except Exception as err:
            log.info(err)
            print(err)

        print(
            ">>> [%s] Finalizando alteração das férias para nova regra 2022 >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
