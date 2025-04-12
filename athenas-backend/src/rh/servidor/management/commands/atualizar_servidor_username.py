# -*- coding: utf-8 -*-

from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger

from rh.servidor.atualizar_infos import AtualizarInfosServidor


log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando faz a atualização de username de Servidores do Athenas em relação ao AD."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--todos",
            action="store_true",
            dest="atualizar_todos_servidores",
            help="Atualização de username de todos os Servidores",
        )

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def set_user_to_job(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        if options["atualizar_todos_servidores"]:
            self.atualizar_todos_servidores()

    def atualizar_todos_servidores(self):
        self.set_user_to_job("job_atualizar_todos_servidores")

        log.info(
            f">>> [{datetime.now()}] Iniciando atualização de username de todos os Servidores."
        )
        try:
            AtualizarInfosServidor().atualizar_username_todos_servidores()
        except Exception as e:
            log.info(
                f">>> [{datetime.now()}] Erro na atualização de username de todos os Servidores"
            )
            log.error(e)

        log.info(
            f">>> [{datetime.now()}] Atualização de username de todos os Servidores concluída."
        )
