# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.const import CANCELED
from rh.dayoff.const import (
    ACQP_FINISHED,
    ACQP_INDEMNIFIED,
    ACQP_PRESCRIBED,
    ACQP_WAIT,
    USU_AUTORIZED_CI,
    USU_CANCELED,
    USU_CHANGED,
    USU_CHANGING,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_INTERRUPTED,
    USU_NOT_AUTHORIZED,
    USU_SOLD,
    USU_SUBSTITUTE,
    USU_SUSPENDED,
    USUFRUCT_STATUS_CHOICE,
)
from rh.dayoff.models import AcquisitionPeriod, Activity

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando irá executar todas as rotinas de atualização do sistema dayoff.
    Todos os usufrutos serão analisados e terão seu status atualizado de acordo com a situação real, ou seja,
    FRUINDO, FRUÍDO, etc. Caso seja atualizado algum usufruto, o período aquisitivo correspodente será analisado e atualizado
    seu @status caso necessite
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--usufruct",
            action="store_true",
            dest="usufruct",
            help="Atualiza os usufrutos!",
        )
        parser.add_argument(
            "-t",
            "--auto_authorization",
            action="store_true",
            dest="auto_authorization",
            help="Roda auto autorização!",
        )
        parser.add_argument(
            "-p",
            "--acquisition_period",
            action="store_true",
            dest="acquisition_period",
            help="Atualiza os períodos aquisitivos!",
        )
        parser.add_argument(
            "-r",
            "--release",
            action="store_true",
            dest="release",
            help="Verifica e libera um período para marcação, caso tenha passado do dia para início da marcação",
        )
        parser.add_argument(
            "-n",
            "--notify",
            action="store_true",
            dest="notify",
            help="Notifica os servidoes que irão fruir férias em XX dias.",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            help="Realiza todas as atualizações!",
        )
        parser.add_argument(
            "-c",
            "--create",
            action="store_true",
            dest="create",
            help="Tenta criar afastamentos de férias não criados!",
        )

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        if options["usufruct"] or options["all"]:
            self.update_usufruct()
        if options["acquisition_period"] or options["all"]:
            self.update_acquisition_period()
        if options["release"] or options["all"]:
            self.release()
        if options["notify"] or options["all"]:
            self.notify_usufruct([30, 7, 1])
        if options["create"] or options["all"]:
            self.create_departure()
        if options["auto_authorization"] or options["all"]:
            self.auto_authorization()

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def update_usufruct(self):
        self.set_user_to_job("job_dayoffctl_update_usufruct")
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando atualizacao automatica dos Usufrutos >>>>>>>>>>>>>"
        )
        for ap in AcquisitionPeriod.objects.exclude(
            status__in=[ACQP_WAIT, ACQP_FINISHED, ACQP_INDEMNIFIED, ACQP_PRESCRIBED]
        ):
            for usu in ap.usufructs.exclude(
                status__in=[
                    USU_AUTORIZED_CI,
                    USU_CHANGING,
                    USU_CHANGED,
                    USU_INTERRUPTED,
                    USU_SUSPENDED,
                    USU_ENJOYED,
                    USU_NOT_AUTHORIZED,
                    USU_SUBSTITUTE,
                    USU_CANCELED,
                    USU_SOLD,
                ]
            ):
                change_status, action = usu._define_status()
                if (
                    action
                    and change_status != usu.status
                    and change_status in (USU_ENJOYING, USU_ENJOYED)
                ):
                    dt = usu.start_date
                    if change_status == USU_ENJOYED:
                        dt = usu.end_date
                    try:
                        print(
                            f"ALTERADO PARA {USUFRUCT_STATUS_CHOICE.get(change_status)}: {ap} >> {DateUtils.date_to_str(dt)}"
                        )
                        usu.transit_status(action, change_status)
                        ap.update_status(update_usufructs=False)
                    except Exception as err:
                        print(ap)
                        print(err)
        print(
            ">>> [%s] Finalizando atualizacao automatica dos Usufrutos >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )

    def update_acquisition_period(self):
        self.set_user_to_job("job_dayoffctl_update_acquisition_period")
        date = datetime.now()
        print(
            ">>> [%s] Iniciando atualizacao automatica dos Períodos Aquisitivos >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
        query = AcquisitionPeriod.objects.filter()
        for ap in query:
            try:
                ap.update_status(update_usufructs=False)
            except Exception as e:
                print(ap, "ERROR", e)
        print(
            ">>> [%s] Finalizando atualizacao automatica dos Períodos Aquisitivos >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )

    def release(self):
        self.set_user_to_job("job_dayoffctl_release")
        date_time = datetime.now()
        for ap in AcquisitionPeriod.objects.all():
            if (
                ap.status == ACQP_WAIT
                and ap.group_period.start_date_book <= date_time.date()
            ):
                ap.release()
                print(
                    ">>> [%s] Finalizando liberacao atualizacao automatica do PA (%s) >>>>>>>>>>>>>"
                    % (DateUtils.datetime_to_str(date_time), ap)
                )

    def notify_usufruct(self, list_days=[]):
        self.set_user_to_job("job_dayoffctl_notify_usufruct")
        Activity.notify_fruition(list_days=list_days)

    def create_departure(self):
        self.set_user_to_job("job_dayoffctl_create_departure")

        from rh.dayoff.signals.departure import manager_departure

        query = Activity.objects.filter(
            Q(usufructs__status__in=[USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED])
            & (
                Q(usufructs__departure__isnull=True)
                | Q(usufructs__departure__estado=CANCELED)
            )
        ).distinct()
        total = query.count()
        count = 0
        print(
            f">>> Iniciando tentativa de criacao de afastamento de dayoff pendentes. {count} de {total}"
        )
        for activity in query:
            count += 1
            print(f">>> Chamando manager_departure para {activity}. {count} de {total}")
            manager_departure(activity)

    def auto_authorization(self):
        self.set_user_to_job("job_dayoffctl_auto_authorization")
        AcquisitionPeriod.auto_authorization()
