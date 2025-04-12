import django
import os
import inspect

from datetime import datetime
from django.core.management.base import BaseCommand
from common.services.scripts.create_job_users import cria_usuarios, cria_usuarios_api
from contrib.utils import getLogger

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """
    Este comando irá criar os usuários que são/serão usados nos JOBs do sistema.
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        if options["all"]:
            self.cria_usuarios_job()

    def cria_usuarios_job(self):
        dt_hr_inicio = datetime.now()
        print(
            f'>>> {dt_hr_inicio.strftime("%d/%m/%Y %H:%M")} Iniciando criação dos usuários de JOBs. >>>>>>>>>>>>>'
        )
        log.info(
            f'>>> {dt_hr_inicio.strftime("%d/%m/%Y %H:%M")} Iniciando criação dos usuários de JOBs. >>>>>>>>>>>>>'
        )

        cria_usuarios()
        cria_usuarios_api()

        dt_hr_fim = datetime.now()
        print(
            f'>>> {dt_hr_inicio.strftime("%d/%m/%Y %H:%M")} - {dt_hr_fim.strftime("%d/%m/%Y %H:%M")} <<< Finalizando criação dos usuários de JOBs. >>>>>>>>>>>>>'
        )
        log.info(
            f'>>> {dt_hr_inicio.strftime("%d/%m/%Y %H:%M")} - {dt_hr_fim.strftime("%d/%m/%Y %H:%M")} <<< Finalizando criação dos usuários de JOBs. >>>>>>>>>>>>>'
        )
