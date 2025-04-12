# -*- coding: utf-8 -*-
import inspect

from datetime import datetime
from contrib.middleware import set_current_user, get_current_user
from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from engine.mq.models import Task

from rh.teletrabalho.tasks import bloquear_tele_pendentes_task
from common.services.models import ScheduledServices
from contrib.utils import getLogger

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá bloquear os teletrabalhos pendentes de envio."""

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        self.set_user_to_job("job_bloquear_mov_teletrabalho")
        self.bloquear_movimentacao_teletrabalho()

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def bloquear_movimentacao_teletrabalho(self):
        dt_hr_inicio = datetime.now()
        log.info(f"Iniciando verificação de bloqueio do teletrabalho | {dt_hr_inicio}")
        class_path = f"{self.__module__}.{self.__class__.__name__}"
        comando = f"{inspect.currentframe().f_code.co_name}"
        servico = ScheduledServices.objects.get(
            classcode__path=class_path, command=comando
        )

        Task.start(
            bloquear_tele_pendentes_task,
            description=f"Verificação de bloqueio do teletrabalho",
            user=get_current_user().id,
        )

        dt_hr_fim = datetime.now()
        log.info(f"Finalizando verificação de bloqueio do teletrabalho | {dt_hr_fim}")
