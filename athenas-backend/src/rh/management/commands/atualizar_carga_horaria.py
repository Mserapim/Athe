# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from datetime import datetime
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from datetime import datetime

from rh.task.hoursworkcontractworkload import (
    atualizar_carga_horaria_batch_task,
    criar_carga_horaria_batch_task,
)

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá atualizar/criar as cargas horárias do servidor vinculando as jornadas."""

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        self.set_user_to_job("athenas")
        self.atualizar_carga_horaria()
        self.criar_carga_horaria()

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def atualizar_carga_horaria(self):
        log.info(f"Iniciando atualização da carga horária | {datetime.now()}")

        user = get_current_user()

        Task.start(
            atualizar_carga_horaria_batch_task,
            description=f"Atualizar carga horária servidor.",
            user=user.id,
        )

        log.info(f"Finalizando atualização da carga horária | {datetime.now()}")

    def criar_carga_horaria(self):
        log.info(f"Iniciando criação da carga horária | {datetime.now()}")

        user = get_current_user()

        Task.start(
            criar_carga_horaria_batch_task,
            description=f"Criar carga horária servidor.",
            user=user.id,
        )

        log.info(f"Finalizando criação da carga horária | {datetime.now()}")
