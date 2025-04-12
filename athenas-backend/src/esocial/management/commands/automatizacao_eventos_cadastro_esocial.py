# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from esocial.models import BatchEvent


log = getLogger(__name__)


class Command(BaseCommand):
    help = """ job para automatizar os eventos de cadastro do esocial """

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):

        self.set_user_to_job("job_automatizacao_eventos_cadastro_esocial")

        log.info("Iniciando o Evento de Cadastro do E-Social")

        try:
            BatchEvent.generate_events_registration_call_task()
        except Exception as e:
            log.exception(e)
        else:
            log.info("Finalizanado o Evento de Cadastro do E-Social")
