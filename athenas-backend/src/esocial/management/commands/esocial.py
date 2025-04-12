# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from contrib.utils import DateUtils
from esocial.models import PayrollPeriod

LEVEL_QUIET = 0
LEVEL_ERROR = 1
LEVEL_INFO = 2
LEVEL_DEBUG = 3

RED = "\033[0;31m"
GREEN = "\033[0;32m"
ORANGE = "\033[0;33m"
WHITE = "\033[1;37m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


class Command(BaseCommand):

    help = """Este comando é responsável por executar rotinas de manutenção da folha de pagamento."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--payroll_period",
            action="store_true",
            dest="payroll_period",
            help="Análise de Períodos (Folhas) e Pendências.",
        )

    def log(self, message):
        (LEVEL_QUIET <= self.verbosity) and print(message)

    def error(self, message):
        (LEVEL_ERROR <= self.verbosity) and print(message)

    def info(self, message):
        (LEVEL_INFO <= self.verbosity) and print(message)

    def debug(self, message):
        (LEVEL_DEBUG <= self.verbosity) and print(message)

    def active_athenas_user(self, user):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist as e:
            self.error('Não econtrei o usuário "%s"' % user)
            raise e
        else:
            set_current_user(user)

    def payroll_period(self, user="athenas"):
        print(
            ">>> [%s] INICIANDO ANÁLISE DE FOLHAS DO ESOCIAL...O RESULTADO SERÁ INFORMADO NAS FOLHAS DO ESOCIAL."
            % DateUtils.datetime_to_str(datetime.now())
        )
        PayrollPeriod.analysis_all_period_call_task()

    def handle(self, payroll_period=None, verbosity=0, user="athenas", **kargs):
        self.verbosity = int(verbosity or 0)
        self.active_athenas_user(user)
        if payroll_period:
            self.payroll_period()
