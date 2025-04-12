# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user, get_current_user
from contrib.utils import getLogger

from engine.mq.models import Task

from rh.folhaponto.tasks_importar_justificativas import (
    importar_justificativas_batch_task,
)


log = getLogger(__name__)


class Command(BaseCommand):
    help = """Script para importar dados de Justificativas do Folha Ponto (banco Oracle - MDC4WEB)
    para o Athenas (módulo registerpoint, tabela MarkPoint)"""

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("job_folhaponto_import_justif")
        self.importar_justificativas()

    def importar_justificativas(self):
        log.info("Iniciando script para importar Folha Ponto Justificativas.")
        user = get_current_user()

        Task.start(
            importar_justificativas_batch_task,
            description=f"Importação de Justificativa do Folha Ponto.",
            user=user.id,
        )
