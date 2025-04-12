# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from datetime import datetime
from django.conf import settings
from contrib.utils import getLogger
from django.db.models.query_utils import Q
from raf.tasks import importing_by_employee
from rh.models import MovimentacaoPosse

log = getLogger("tasker")


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "--instance",
            default=None,
            type=int,
            dest="instance",
            help="""Define a instância de importação.""",
        ),
        make_option(
            "--initial-date",
            default=datetime.fromordinal(datetime.today().toordinal() - 1).date(),
            dest="initial_date",
            help="""Data inicial do período de importação.
            Define a data de ontem como valor default.
            Formato: yyyy-mm-dd""",
        ),
        make_option(
            "--final-date",
            default=datetime.fromordinal(datetime.today().toordinal() - 1).date(),
            dest="final_date",
            help="""Data final do período de importação.
            Define a data de ontem como valor default.
            Formato: yyyy-mm-dd""",
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
        make_option(
            "--production-server",
            default=False,
            action="store_true",
            dest="production_server",
            help="""Não executa os comandos de inserção no Banco de Dados.
            Default: False""",
        ),
    )

    def handle(
        self,
        initial_date,
        final_date,
        registration,
        production_server,
        instance,
        no_insert,
        *args,
        **kargs
    ):
        WS_EPROC_URL_1 = (
            getattr(settings, "WS_EPROC_PROD_URL_1", None)
            if production_server
            else getattr(settings, "WS_EPROC_TREI_URL_1", None)
        )
        WS_EPROC_URL_2 = (
            getattr(settings, "WS_EPROC_PROD_URL_2", None)
            if production_server
            else getattr(settings, "WS_EPROC_TREI_URL_2", None)
        )
        date_initial = datetime.strptime(initial_date, "%Y-%m-%d").date()
        date_final = datetime.strptime(final_date, "%Y-%m-%d").date()
        list_of_employees = (
            MovimentacaoPosse.objects.filter(servidor__tipo="M")
            .filter(
                Q(data_desligamento__isnull=True)
                | (
                    Q(data_desligamento__gte=date_initial)
                    & Q(data_desligamento__lte=date_final)
                )
            )
            .order_by("servidor__pessoa_fisica__nome")
            .distinct("servidor__pessoa_fisica__nome")
        )
        if registration:
            list_of_employees = list_of_employees.filter(
                servidor__matricula=registration
            )
        for membro in list_of_employees:
            if instance == 1 or instance is None:
                importing_by_employee.delay(
                    initial_date,
                    final_date,
                    membro.servidor.matricula,
                    WS_EPROC_URL_1,
                    1,
                    no_insert,
                )
            if instance == 2 or instance is None:
                importing_by_employee.delay(
                    initial_date,
                    final_date,
                    membro.servidor.matricula,
                    WS_EPROC_URL_2,
                    2,
                    no_insert,
                )
