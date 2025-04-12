# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from contrib.utils import getLogger

log = getLogger("tasker")
from rh.models import Servidor
from raf.tasks import processing_by_employee


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            "--month",
            dest="month",
            help="""Mês de referência para aferimento do RAF.
            Formato: mm""",
        ),
        make_option(
            "--year",
            dest="year",
            help="""Ano de referência para aferimento do RAF.
            Formato: yyyy""",
        ),
        make_option(
            "--registration",
            default=None,
            dest="registration",
            help="""Matrícula do membro que terá os dados importados.
            Default: None""",
        ),
        make_option(
            "--no-insert",
            default=False,
            action="store_true",
            dest="no_insert",
            help="""Não executa os comandos de inserção no Banco de Dados.
            Default: False""",
        ),
    )

    def handle(self, month, year, registration, no_insert, *args, **kargs):
        if registration:
            processing_by_employee.delay(registration, month, year)
        else:
            list_of_employees = Servidor.objects.filter(tipo="M", ativo=True)
            for membro in list_of_employees:
                processing_by_employee.delay(membro.matricula, month, year)
