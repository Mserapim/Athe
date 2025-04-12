# -*- coding: utf-8 -*-

from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger

from engine.mq.models import Task
from nomeacao.cadastramento.tasks_sinc_form_nomeacao_residente import (
    sinc_form_cpf_nomeacao_residente_task,
)

log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando faz a sincronização com o formulário para Nomeação."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--residentes",
            action="store_true",
            dest="sinc_residentes",
            help="Sincronização com o formulário para Nomeação de Residentes",
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
        self.sinc_form_nomeacao_residente()

    def sinc_form_nomeacao_residente(self):
        self.set_user_to_job("job_sinc_form_nomeacao_residentes")

        log.info(
            f">>> [{datetime.now()}] Iniciando sincronização com o formulário para nomeação de Residentes."
        )
        try:
            Task.start(
                sinc_form_cpf_nomeacao_residente_task,
                description=f"Processamento para sincronizar CPFs à nomeação de residente.",
                user=get_current_user().pk,
            )
        except Exception as e:
            log.error(e)
        log.info(
            f">>> [{datetime.now()}] Iniciando sincronização com o formulário para nomeação de Residentes >>>>>>>>>>>>>"
        )
