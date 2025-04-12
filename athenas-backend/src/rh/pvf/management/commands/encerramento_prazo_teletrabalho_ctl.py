# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from datetime import datetime
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.pvf.apiv2.utils.telework import notifica_encerramento_tele

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá acionar a função que enviará as notificações por e-mail sobre o encerramento do prazo de 
            envio do teletrabalho."""

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        self.set_user_to_job("job_encerramento_prazo_teletrabalho")
        self.encerramento_prazo_teletrabalho()

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def encerramento_prazo_teletrabalho(self):
        log.info(
            f"Iniciando notificações por e-mail sobre o encerramento do prazo de envio do teletrabalho | {datetime.now()}"
        )
        notifica_encerramento_tele()
        log.info(
            f"Finalizando notificações por e-mail sobre o encerramento do prazo de envio do teletrabalho | {datetime.now()}"
        )
