# -*- coding: utf-8 -*-

import argparse
import re
import sys
import time
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from contrib.utils import DateUtils
from engine.mq.models import Task
from rh.gfp.models import Folha, Periodo
from rh.gfp.tasks import (
    management_remuneration_bases,
    process_evaluation_differences_payroll,
)

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


def period_regex(arg_value, pat=re.compile(r"^[0-9]{2}/[0-9]{4}$")):
    if arg_value and not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value")
    return arg_value


class Command(BaseCommand):

    help = """Este comando é responsável por executar rotinas de manutenção da folha de pagamento."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--payroll",
            type=int,
            dest="payroll",
            help="ID da folha a ser avaliada",
        )
        parser.add_argument(
            "-t",
            "--type_payroll",
            type=int,
            dest="type_payroll",
            help="ID do tipo de folha a ser avaliada",
        )
        parser.add_argument(
            "-e",
            "--events",
            type=str,
            dest="events",
            help="Número dos eventos a serem avaliados as diferenças. Ex.: 00100,00400,01700",
        )
        parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            dest="list_payrolls",
            help="Lista o ID das útimas QNT folhas",
            default=False,
        )
        parser.add_argument(
            "-n",
            "--qnt",
            type=int,
            dest="qnt",
            help="Quantidade de folhas a serem listadas. Default=10",
            default=13,
        )
        parser.add_argument(
            "-c",
            "--check",
            action="store_true",
            dest="check",
            help="Checar e avaliar folha para o fechamento/processamento",
        )
        parser.add_argument(
            "-b",
            "--base",
            action="store_true",
            dest="only_base",
            help="Avaliar apenas folhas base, descartando as complementares!",
        )
        parser.add_argument(
            "-d",
            "--diffs",
            action="store_true",
            dest="diffs",
            help="Gerar as diferenças dos últimos n periodos!",
        )
        parser.add_argument(
            "-u",
            "--user",
            type=str,
            dest="user",
            help="Usuário utilizado no processamento!",
            default="athenas",
        )
        parser.add_argument(
            "-i",
            "--initial",
            type=period_regex,
            dest="initial",
            help="Período inicial de processamento!",
            default="",
        )
        parser.add_argument(
            "-f",
            "--final",
            type=period_regex,
            dest="final",
            help="Período final de processamento!",
            default="",
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

    def check_payroll(self, payroll_id):
        payroll = Folha.objects.get(pk=payroll_id)
        print(
            f">>> CONSOLIDANDO CONTRACHEQUES PARA {payroll} (\033[93m AGUARDE...\033[0m) [0.0%%]",
            end="",
        )
        total = payroll.paychecks.all().count()
        if total == 0:
            total = 1
        count = 0
        for paycheck in payroll.paychecks.all():
            count += 1
            print(
                ">>> CONSOLIDANDO CONTRACHEQUES PARA %s (\033[93m AGUARDE...\033[0m) [%0.1f%%]"
                % (payroll, (count * 100.0 / total)),
                end="",
            )

        print("")

        print(">>> VERIFICANDO CONTRACHEQUES NEGATIVOS")
        for paycheck in payroll.paychecks.filter(total_liquido__lt=0):
            print(
                "     %s >> \033[91m%0.2f\033[0m" % (paycheck, paycheck.total_liquido)
            )

    def list_payrolls(self, qnt=13, type_payroll=None):

        print(">>> LISTANDO FOLHAS POR ID")
        query = Folha.objects.order_by("periodo", "-pk")
        if type_payroll:
            query = query.filter(tipo_folha=type_payroll)

        c_periodos = qnt
        pp = query.first().periodo.pk if query.first() else 0
        for f in query:
            print(
                "    ID \033[94m%s\033[0m(\033[94m%s\033[0m) > %s"
                % (f.id, f.tipo_folha.id, f)
            )
            if pp != f.periodo.pk:
                c_periodos -= 1
                pp = f.periodo.pk
            if c_periodos <= 0:
                break

    def evaluate_differences(
        self,
        qnt=13,
        type_payroll=None,
        events=[],
        payroll=None,
        initial="",
        final="",
        only_base=False,
        user="athenas",
    ):
        print(
            ">>> [%s] VERIFICANDO DIFERENÇAS NOS CONTRACHEQUES... (\033[93mAguarde, pode demorar um pouco!\033[0m)"
            % DateUtils.datetime_to_str(datetime.now())
        )
        print(initial, final, qnt)
        payrolls = Folha.objects.filter(status__in=[3, 4]).order_by("periodo", "-pk")
        periods = Periodo.objects.all()
        start_period = periods[qnt - 1]
        final_period = periods[0]
        if final:
            p_year = int(final[3:])
            p_month = int(final[0:2])
            final_period = (
                periods.filter(ano=p_year, mes=p_month).last() or final_period
            )
            if not initial:
                period = final_period.previous_period(qnt)
                start_period = period or start_period

        if initial:
            p_year = int(initial[3:])
            p_month = int(initial[0:2])
            start_period = (
                periods.filter(ano=p_year, mes=p_month).last() or start_period
            )
            if not final:
                period = start_period.next_period(qnt)
                final_period = period or final_period

        if type_payroll:
            payrolls = payrolls.filter(tipo_folha=type_payroll)

        if payroll:
            payrolls = payrolls.filter(pk=payroll)

        if only_base:
            payrolls = payrolls.filter(complement=0)

        if payrolls.exists():
            print(f"{start_period} > {final_period}")

        period = start_period
        while period and period <= final_period:
            # print(f'>> {period}')
            task_bases = Task.start(
                management_remuneration_bases,
                description=f"Avaliando bases de remuneração por período {period}",
                period_id=period.pk,
                user=user,
            )
            while not Task.objects.get(pk=task_bases.pk).executed:
                # print('>>> TASK %s - %s' % (task.uuid, Task.objects.get(pk=task.pk).state))
                time.sleep(2)

            for p in payrolls.filter(periodo=period):

                print(
                    f"> \033[94m{p}\033[0m", end="", flush=True
                )  # task, hook, payroll, user, number_events=[]
                t1 = time.time()

                task = Task.start(
                    process_evaluation_differences_payroll,
                    description="Avaliando diferenças em %s" % p,
                    payroll_id=p.pk,
                    user=user,
                    number_events=events,
                )
                # uuid = 0
                uuid = task.uuid
                while not Task.objects.get(pk=task.pk).executed:
                    # print('>>> TASK %s - %s' % (task.uuid, Task.objects.get(pk=task.pk).state))
                    time.sleep(2)

                elapsed_time = time.time() - t1
                print(f" {timedelta(seconds=elapsed_time)} ({uuid})")
                # print('>>> TASK %s - %s' % (task.uuid, Task.objects.get(pk=task.pk).state))
                # process_evaluation_differences_payroll.delay()
                # p.evaluate_differences(number_events=events)
                # if pp != p.periodo.pk:
                #     c_periodos -= 1
                #     pp = p.periodo.pk
                # if c_periodos <= 0:
                #     break
            period = period.next

        print(
            ">>> [%s] FINALIZANDO DIFERENÇAS"
            % DateUtils.datetime_to_str(datetime.now())
        )

    def handle(
        self,
        payroll=None,
        type_payroll=None,
        check=False,
        verbosity=0,
        list_payrolls=False,
        qnt=13,
        diffs=False,
        events="",
        user="athenas",
        initial="",
        final="",
        only_base=False,
        **kargs,
    ):
        self.verbosity = int(verbosity or 0)
        self.active_athenas_user(user)
        number_events = []
        if events:
            number_events = events.split(",")
        if list_payrolls:
            self.list_payrolls(qnt, type_payroll)
        if check:
            self.check_payroll(payroll)
        if diffs:
            self.evaluate_differences(
                qnt,
                type_payroll,
                events=number_events,
                payroll=payroll,
                initial=initial,
                final=final,
                only_base=only_base,
            )
