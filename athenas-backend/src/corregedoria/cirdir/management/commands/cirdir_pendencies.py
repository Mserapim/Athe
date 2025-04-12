# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from corregedoria.cirdir.models import ControlInformation


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "--check",
            default=None,
            action="store_true",
            dest="check",
            help="""Realiza checagem das pendencias do dbvr/srdir""",
        )

        parser.add_argument(
            "--year",
            dest="year",
            required=False,
            help="Ano base para verificar pendência",
        )

        parser.add_argument(
            "--all",
            dest="all",
            default=None,
            action="store_true",
            help="Verifica pendência em todos os registros.",
        )

    def _exec_actions(self, year, all):
        print("Executando checagem de pendencias")

        if all:
            srdirs = ControlInformation.objects.filter(hidden=False)
        else:
            srdirs = ControlInformation.objects.filter(hidden=False, year=year)

        print(f"Serão processados {srdirs.count()} registros")

        for srdir in srdirs:
            srdir.pendencies_check()

        print("Finalizando acao.")

    def handle(self, check, year, all, *args, **kwargs):
        if check:
            self._exec_actions(year, all)
