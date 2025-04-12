# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from datetime import datetime
from raf.models import *
from rh.models import *
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger

log = getLogger("db")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--month",
            default=None,
            type=int,
            dest="month",
            help="""Mês de referência do RAF.""",
        )

        parser.add_argument(
            "--year",
            default=None,
            type=int,
            dest="year",
            help="""Ano de referência do RAF.""",
        )

        parser.add_argument(
            "--registration",
            default=None,
            dest="registration",
            help="""Matrícula do membro do RAF.""",
        )

        parser.add_argument(
            "--add-worklocation",
            default=None,
            dest="worklocation",
            help="""Operação de fechamento do RAF.""",
        )

        parser.add_argument(
            "--exec-actions",
            default=None,
            action="store_true",
            dest="execactions",
            help="""Executada as ações agendadas para o dia específico.""",
        )

        parser.add_argument(
            "--open",
            default=False,
            action="store_true",
            dest="open",
            help="""Operação de abertura do RAF. Efetuado somente em conjunto com a opção --registration.""",
        )

        parser.add_argument(
            "--close",
            default=False,
            action="store_true",
            dest="close",
            help="""Operação de fechamento do RAF. Efetuado somente em conjunto com a opção --registration.""",
        )

        parser.add_argument(
            "--unsubmitted",
            default=False,
            action="store_true",
            dest="unsubmitted",
            help="""Operação para desfazer a submissão do RAF. Efetuado somente em conjunto com a opção --registration.""",
        )

    def _open_raf(self, open, raf):
        if open:
            # print u'Abrindo RAF %s...' % raf
            raf.closed = False
            raf.save()

    def _close_raf(self, close, raf):
        if close:
            # print u'Fechando RAF %s...' % raf
            raf.closed = True
            raf.save()

    def _unsubmitted_raf(self, registration, unsubmitted, raf):
        if registration and unsubmitted:
            # print u'Desfazendo submissão do RAF %s...' % raf
            raf.submitted_by = None
            raf.submitted_at = None
            raf.save()

    def _add_worklocation(self, registration, worklocation, raf):
        if registration and worklocation:
            location = Lotacao.objects.filter(id=worklocation).first()
            if location:
                # print u'Adicionando %s no RAF %s...' % (location, raf)
                workerlocation = WorkerLocation()
                workerlocation.raf = raf
                workerlocation.location = location
                workerlocation.save()

    def _execactions(self):
        today = datetime.today().date()
        rafs = FunctionalActivityReport.objects.filter(open_date=today)
        for raf in rafs:
            if raf.departure is False:
                raf.open()
        rafs = FunctionalActivityReport.objects.filter(close_date=today)
        for raf in rafs:
            raf.close()

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(
        self,
        month,
        year,
        registration,
        worklocation,
        execactions,
        open,
        close,
        unsubmitted,
        *args,
        **kargs,
    ):
        self.set_user_to_job("job_raf_admin_handle")
        if execactions is True:
            self._execactions()
        else:
            list_of_employees = Servidor.objects.filter(tipo="M")
            if registration:
                list_of_employees = list_of_employees.filter(matricula=registration)
            for membro in list_of_employees:
                raf = FunctionalActivityReport.objects.filter(
                    employee=membro, month=month, year=year
                ).first()
                if raf:
                    self._open_raf(open=open, raf=raf)
                    self._close_raf(close=close, raf=raf)
                    self._unsubmitted_raf(
                        registration=registration, unsubmitted=unsubmitted, raf=raf
                    )
                    self._add_worklocation(
                        registration=registration, worklocation=worklocation, raf=raf
                    )
                else:
                    pass
