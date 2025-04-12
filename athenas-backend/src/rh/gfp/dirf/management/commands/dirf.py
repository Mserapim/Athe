# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from datetime import datetime
from optparse import make_option
from time import time

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from future.builtins import str

# from adm.diarias.models import MovimentoFinanceiro, Solicitacao
from contrib.middleware import StartupLoader, set_current_user
from contrib.utils import DateUtils
from rh.models import Pessoa as Person
from standard.models import Choice, Configuration
from workflow.models import Vertex, Workflow
from rh.gfp.dirf.models import DirfSummary, NaturezaRendimento

LEVEL_QUIET = 0
LEVEL_ERROR = 1
LEVEL_INFO = 2
LEVEL_DEBUG = 3

if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


class Command(BaseCommand):

    help = """Este comando é responsável por executar rotinas de manutenção do modulo da DIRF."""

    def add_arguments(self, parser):
        # parser.add_argument(
        #     '-d',
        #     '--diarias',
        #     action='store_true',
        #     dest='diarias',
        #     help='Faz a totalização das diárias para o ano corrente ou para o ano passado como parametro no formato XXXX',
        #     default=False
        # )
        parser.add_argument(
            "-y",
            "--year",
            dest="year",
            help="Definir o ano a ser sumarizado as diárias para a DIRF. formato XXXX",
            default=datetime.now().year,
        )
        parser.add_argument(
            "-u",
            "--user",
            dest="user",
            help="Passa o usuário que deve executar a rotina. default=athenas",
            default="athenas",
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
        print(message)

    def active_athenas_user(self):
        try:
            user = User.objects.get(username="athenas")
        except User.DoesNotExist as e:
            self.error('Não econtrei o usuário "athenas"')
            raise e
        else:
            set_current_user(user)

    # def handle(self, diarias, user, *args, **kargs):
    #     self.verbosity = int(verbosity or 0)
    #     self.active_athenas_user()

    #     StartupLoader().doLoad()
    #     with_start and self.do_start()
    #     with_end and self.do_end()
    #     with_close and self.do_close()
    #     recalc is not None and self.do_recalc(recalc)
    #     position is not None and self.do_position(*position.split(':'))

    def handle(self, diarias, year, user, verbosity, *args, **kargs):
        self.verbosity = int(verbosity or 0)
        current_year = datetime.now().year
        # year = current_year if not diarias else int(diarias)
        print("%s %s %s > %s" % (diarias, year, user, current_year))

        # if diarias:
        #     self.summarize_daily(year)

    def summarize_daily_month(self, query, year, month):
        found = []
        query_month = query.filter(data_ordem__month=month).annotate(
            total_diaria=Sum("valor_diaria"),
            total_transporte=Sum("auxilio_transporte"),
            total_auxilio_alimentacao=Sum("desconto_auxilio_alimentacao"),
        )
        choice_dirf = Choice.objects.get(
            app_label="dirf", name="IDENTIFIERS_DIRF", label="BPFDEC-RIDAC"
        )
        code = NaturezaRendimento.objects.get(codigo="0561")
        print("Totalizando diárias para mês %02d" % (month))
        print("Encontrado pagamento para %d pessoa(s)" % query_month.count())
        for mf in query_month:
            pessoa = Person.objects.get(pk=mf.get("participante__pessoa"))
            total_diaria = float(mf.get("total_diaria", 0) or 0)
            total_transporte = float(mf.get("total_transporte", 0) or 0)
            total_auxilio_alimentacao = float(
                mf.get("total_auxilio_alimentacao", 0) or 0
            )

            dsd, created = DirfSummary.objects.get_or_create(
                person=pessoa,
                calendar_year=year,
                info="DIARIA",
                identifier=choice_dirf.value,
                code=code,
            )
            setattr(dsd, "value_%02d" % month, total_diaria - total_auxilio_alimentacao)
            dsd.save()
            found.append(dsd.pk)

            dsa, created = DirfSummary.objects.get_or_create(
                person=pessoa,
                calendar_year=year,
                info="AJUDA-TRANSPORTE",
                identifier=choice_dirf.value,
                code=code,
            )
            setattr(dsa, "value_%02d" % month, total_transporte)
            dsa.save()
            found.append(dsa.pk)
        return found

    # def summarize_daily(self, year):
    #     year = int(year)
    #     query = MovimentoFinanceiro.objects.filter(
    #         data_ordem__year=year,
    #     ).order_by(
    #         'participante__pessoa__nome'
    #     ).values(
    #         'participante__pessoa'
    #     )
    #     current_year = datetime.now().year


#
#     max_month = 12
#     if year == current_year:
#         max_month = datetime.now().month
#     elif year > current_year:
#         max_month = 0
#     print('Encontrado pagamento para %d pessoa(s)! %02d/%04d' % (query.count(), max_month, year))
#     month = 1
#     while month < (max_month + 1):
#         self.summarize_daily_month(query, year, month)
#         month += 1
