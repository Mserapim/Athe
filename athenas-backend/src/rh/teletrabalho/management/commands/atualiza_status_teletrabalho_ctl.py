# -*- coding: utf-8 -*-
from datetime import datetime
from contrib.middleware import set_current_user, get_current_user
from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from rh.models import MovimentacaoTeletrabalho
from engine.mq.models import Task

from rh.teletrabalho.tasks import atualiza_status_teletrabalho_task
from contrib.utils import getLogger

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá atualizar o status de todos os teletrabalhos de acordo com a data atual."""

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        self.set_user_to_job("job_atualiza_status_teletrabalho")
        self.atualiza_status_teletrabalho()

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def atualiza_status_teletrabalho(self):
        log.info(f"Iniciando atualização do status do teletrabalho | {datetime.now()}")
        for tele in MovimentacaoTeletrabalho.objects.all():
            tele.validar_teletrabalho_ativo()
            query = MovimentacaoTeletrabalho.objects.filter(pk=tele.pk)
            if tele.ativo != query.first().ativo:
                Task.start(
                    atualiza_status_teletrabalho_task,
                    description=f"Notificação teletrabalho",
                    tele_pk=tele.pk,
                    ativo=tele.ativo,
                    user=get_current_user().id,
                )
        log.info(
            f"Finalizando atualização do status do teletrabalho | {datetime.now()}"
        )
