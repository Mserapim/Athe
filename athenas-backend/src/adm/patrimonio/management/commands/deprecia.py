# -*- coding: utf-8 -*-
from datetime import datetime

from adm.patrimonio.models import Avaliacao
from contrib.middleware import StartupLoader, set_current_user
from contrib.utils import DateUtils, getLogger
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

LEVEL_QUIET = 0
LEVEL_ERROR = 1
LEVEL_INFO = 2
LEVEL_DEBUG = 3

log = getLogger(__name__)


class Command(BaseCommand):

    help = """Este comando é responsável por executar rotinas de manutenção do modulo de diárias."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--mes",
            type=int,
            default=0,
            dest="mes",
            help="Mes de competencia para depreciação",
        )

        parser.add_argument(
            "-a",
            "--ano",
            type=int,
            default=0,
            dest="ano",
            help="Ano de competencia para depreciação",
        )

        parser.add_argument(
            "--de",
            dest="de",
            help="Data de inicio para base no cadastro de tombos a depreciar, formato YYYY-MM-DD",
        )

        parser.add_argument(
            "--ate",
            dest="ate",
            help="Data de fim para base no cadastro de tombos a depreciar, formato YYYY-MM-DD",
        )

        parser.add_argument(
            "--execute",
            dest="execute",
            action="store_true",
            help="Fazer analize e execução da depreciação.",
        )

    def log(self, message):
        (LEVEL_QUIET <= self.verbosity) and self.print_message(message)

    def error(self, message):
        (LEVEL_ERROR <= self.verbosity) and self.print_message(message)

    def info(self, message):
        (LEVEL_INFO <= self.verbosity) and self.print_message(message)

    def debug(self, message):
        (LEVEL_DEBUG <= self.verbosity) and self.print_message(message)

    def print_message(self, message):
        try:
            print(message)
        except Exception:
            print("ENCODE ERROR")

    def active_athenas_user(self):
        try:
            user = User.objects.get(username="athenas")
        except User.DoesNotExist as e:
            self.error('Não econtrei o usuário "athenas"')
            raise e
        else:
            set_current_user(user)

    def handle(
        self, mes=None, ano=None, verbosity=0, de=None, ate=None, execute=False, **kargs
    ):
        self.verbosity = int(verbosity or 0)
        self.active_athenas_user()

        StartupLoader().doLoad()
        avaliacao = None

        if mes == 0 or ano == 0:
            basedate = datetime.now() - relativedelta(months=1)
            ano = basedate.year
            mes = basedate.month

        try:
            avaliacao = Avaliacao.objects.get(mes=mes, ano=ano, tipo=1)
        except Avaliacao.DoesNotExist:
            avaliacao = Avaliacao(mes=mes, ano=ano, tipo=1)
        finally:
            self.log("Avaliacao %s" % avaliacao)
            if de is not None:
                passed_date = DateUtils.str_to_date(de, "%Y-%m-%d")
                avaliacao.de = datetime(
                    passed_date.year, passed_date.month, passed_date.day, 0, 0, 0
                )

            if ate is not None:
                passed_date = DateUtils.str_to_date(de, "%Y-%m-%d")
                avaliacao.ate = datetime(
                    passed_date.year, passed_date.month, passed_date.day, 23, 59, 59
                )
            else:
                avaliacao.ate = (
                    datetime(ano, mes, 1, 0, 0, 0) + relativedelta(months=1)
                ) - relativedelta(seconds=1)

            try:
                self.log(
                    "Analizando itens adequiridos entre %s até %s"
                    % (avaliacao.de, avaliacao.ate)
                )
                self.log(
                    "Referência: %s"
                    % "/".join([str(avaliacao.mes), str(avaliacao.ano)])
                )
                avaliacao.without_task = True
                avaliacao.save()
                avaliacao.analize(execute)
            except Exception as e:
                log.exception(e)
                self.log(e)
