# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.models import AcquisitionPeriod
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rh.pvf.const import RESIDENTS_RECESS
from rh.dayoff.const import ACQP_PROGRESS
from rh.dayoff.models import ActivityBook
from contrib.daterange import NewDateRange
from common.util.send_email import EmailNotification
from standard.models import EmailTemplate


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """
        Este comando irá executar uma rotina mensal que notifica e agenda o recesso de residentes
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.resident_scheduling_recess()
        self.notify_resident_scheduled_recess()

    def resident_scheduling_recess(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando rotina de agendamento de recesso de residentes nos último 30 dias >>>>>>>>>>>>>"
        )
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando rotina de agendamento de recesso de residentes nos último 30 dias >>>>>>>>>>>>>"
        )

        for acq_period in AcquisitionPeriod.objects.filter(
            employee__ativo=True,
            status=ACQP_PROGRESS,
            days_not_booked_cache__gt=0,
            start_date_fruition__lte=date.date(),
            end_date_fruition__gt=date.date(),
            group_period__configuration__sub_type_of_usufruct__in=[RESIDENTS_RECESS],
        ):
            try:
                employee = acq_period.employee
                dt_exercise = employee.exercise_date
                diffs = date.date() - dt_exercise
                qtd_months = diffs.days // 30
                if qtd_months in [15, 23]:
                    start_date = (
                        acq_period.end_date_fruition - timedelta(days=30)
                    ) + timedelta(days=1)
                    end_date = (
                        start_date + timedelta(days=acq_period.days_not_booked_cache)
                    ) - timedelta(days=1)
                    if (
                        start_date
                        and end_date
                        and acq_period.employee.termination_date >= end_date
                        and start_date >= date.date()
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
                        template_email = EmailTemplate.objects.get(
                            code="AGENDAMENTO_RECESSO_RESIDENTES"
                        )
                        receivers = [
                            {
                                "email": employee.pessoa_fisica.email_institucional,
                                "nome": employee.pessoa_fisica.nome,
                                "idUsuario": employee.id_usuario_mastiff,
                            }
                        ]
                        subject = template_email.subject
                        contents = (
                            template_email.contents.replace(
                                "%referencia%",
                                str(acq_period.group_period.year_reference),
                            )
                            .replace("%start%", start_date.strftime("%d/%m/%Y"))
                            .replace("%end%", end_date.strftime("%d/%m/%Y"))
                        )
                        EmailNotification().send_email_default(
                            receivers, subject, contents
                        )

            except Exception as err:
                log.info(err)
                print(err)

        log.info(
            ">>> [%s] Finalizando rotina de agendamento de recesso de residentes nos último 30 dias >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
        print(
            ">>> [%s] Finalizando rotina de agendamento de recesso de residentes nos último 30 dias >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )

    def notify_resident_scheduled_recess(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando rotina de notificação de recesso de residentes >>>>>>>>>>>>>"
        )
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando rotina de notificação de recesso de residentes >>>>>>>>>>>>>"
        )

        for acq_period in (
            AcquisitionPeriod.objects.filter(
                employee__ativo=True,
                status=ACQP_PROGRESS,
                days_not_booked_cache__gt=0,
                start_date_fruition__lte=date.date(),
                end_date_fruition__gt=date.date(),
                group_period__configuration__sub_type_of_usufruct__in=[
                    RESIDENTS_RECESS
                ],
            )
            .order_by("employee__matricula")
            .distinct("employee__matricula")
        ):
            try:
                employee = acq_period.employee
                supervisor = employee.chefe_imediato
                dt_exercise = employee.exercise_date
                date_reference = dt_exercise + relativedelta(months=12)
                date_two_month = date_reference + relativedelta(months=1)
                date_tree_month = date_reference + relativedelta(months=2)
                date_first_2_month = date_reference + relativedelta(months=8)
                date_two_2_month = date_reference + relativedelta(months=9)
                date_tree_2_month = date_reference + relativedelta(months=10)

                if date.date() in [
                    date_reference,
                    date_two_month,
                    date_tree_month,
                    date_first_2_month,
                    date_two_2_month,
                    date_tree_2_month,
                ]:
                    dt_recess = (
                        acq_period.end_date_fruition - timedelta(days=30)
                    ) + timedelta(days=1)

                    # Envio de notificação para o residente
                    intern_template_email = EmailTemplate.objects.get(
                        code="NOTIFICAO_RECESSO_RESIDENTE"
                    )
                    intern_receivers = [
                        {
                            "email": employee.pessoa_fisica.email_institucional,
                            "nome": employee.pessoa_fisica.nome,
                            "idUsuario": employee.id_usuario_mastiff,
                        }
                    ]
                    subject = intern_template_email.subject
                    contents = intern_template_email.contents.replace(
                        "%data%", dt_recess.strftime("%d/%m/%Y")
                    )

                    log.info(f"Notificação enviada: {employee.pessoa_fisica.nome}")
                    EmailNotification().send_email_default(
                        intern_receivers, subject, contents
                    )

                    # Envio de notificação para supervidor do residente
                    supervidor_template_email = EmailTemplate.objects.get(
                        code="SUPERVISOR_NOTIFICAO_RECESSO_RESIDENTE"
                    )
                    supervisor_receivers = [
                        {
                            "email": supervisor.pessoa_fisica.email_institucional,
                            "nome": supervisor.pessoa_fisica.nome,
                            "idUsuario": supervisor.id_usuario_mastiff,
                        }
                    ]
                    subject = supervidor_template_email.subject
                    contents = supervidor_template_email.contents.replace(
                        "%data%", dt_recess.strftime("%d/%m/%Y")
                    ).replace("%residente%", employee.pessoa_fisica.nome)

                    EmailNotification().send_email_default(
                        supervisor_receivers, subject, contents
                    )
                    log.info(f"Notificação enviada: {supervisor.pessoa_fisica.nome}")

            except Exception as err:
                log.info(err)
                print(err)

        log.info(
            ">>> [%s] Finalizando rotina de notificação de recesso de residentes >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
        print(
            ">>> [%s] Finalizando rotina de notificação de recesso de residentes >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
