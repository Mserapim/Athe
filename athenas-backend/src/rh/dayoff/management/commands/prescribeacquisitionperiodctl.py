# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.models import Configuration, AcquisitionPeriod

log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando verifica diariamente se a data fim do anexo do período aquisitivo é superior a
              data início + dias para prescrição (configuração de usufrutos e folgas), se sim, deve
              alterar o status para Prescrito.
              - Somente executar para anexos vinculados a configuração onde o valor é maior que zero.
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.change_status_acquisition_period()

    def change_status_acquisition_period(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando alteração do status dos anexos dos Períodos Aquisitivos >>>>>>>>>>>>>"
        )
        try:
            configurations = Configuration.objects.filter(prescription_days__gt=0)
            acquisition_periods = AcquisitionPeriod.objects.filter(
                group_period__configuration__in=configurations
            )
            for acquisition_period in acquisition_periods:
                if (
                    acquisition_period.exist_active_attachment()
                    and acquisition_period.days > 0
                ):
                    prescription_days = (
                        acquisition_period.group_period.configuration.prescription_days
                    )
                    for (
                        attachment
                    ) in acquisition_period.attachment_acquisitionperiod.all():
                        date_with_prescription = attachment.date_start + timedelta(
                            days=prescription_days
                        )
                        if (
                            attachment.date_end > date_with_prescription
                            and attachment.status != 2
                        ):
                            attachment.status = 2
                            attachment.save()
                            print(
                                f">>> >>> Anexo: [ID {attachment.id} | {attachment}] status alterado para Prescrito >>>>>>>>>>>>>"
                            )

        except Exception as err:
            log.info(err)
            print(err)
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Finalizando alteração do status dos anexos dos Períodos Aquisitivos >>>>>>>>>>>>>"
        )
