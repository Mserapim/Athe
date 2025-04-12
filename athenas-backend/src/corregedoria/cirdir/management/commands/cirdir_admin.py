# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from datetime import datetime, timedelta
from corregedoria.cirdir.models import ControlInformation
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger

log = getLogger("db")


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "--exec-actions",
            default=None,
            action="store_true",
            dest="exec_actions",
            help="""Executada as ações agendadas para o dia configurado no gestor do srdir.""",
        )

        parser.add_argument(
            "--user",
            dest="user",
            required=True,
            help="Usuário que sera utilizado para gerar executar a ação",
        )

    def _exec_actions(self, user):
        print("Executando acoes para o SRDIR - {}".format(datetime.today()))
        if user == "athenas":
            username = "job_cirdir__exec_actions"
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as e:
                log.error(f'Não foi localizado o usuário  "{username}" - {e}')
                set_current_user(User.objects.get(username="athenas"))
            else:
                set_current_user(user)
        else:
            set_current_user(user)
        year = (datetime.today() - timedelta(days=1)).year

        srdirs = ControlInformation.objects.filter(year=year)
        for srdir in srdirs:
            srdir.exec_schedule(saving=True, signal=False)

        print("Finalizando acoes agendadas no SRDIR.")

    def handle(self, exec_actions, user, *args, **kwargs):
        if exec_actions is True:
            self._exec_actions(user)
