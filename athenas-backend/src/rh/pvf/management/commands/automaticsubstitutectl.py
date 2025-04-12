# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rh.pvf.utils.pvf_automatic_substitute import automatic_substitute_acknowledgment
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger

log = getLogger("db")


class Command(BaseCommand):
    help = """Esse Comando verifica se transcorrido decorreu o prazo para o substituto dar ciência em um afastamento/usufruto e em caso positivo,
    dá a ciência automática. """

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("job_automaticsubstitutectl_acknowledgment_automatic")
        self.acknowledgment_automatic()

    def acknowledgment_automatic(self):
        date = datetime.now()
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando verificação do prazo para ciência dos substitutos >>>>>>>>>>>>>"
        )
        try:
            automatic_substitute_acknowledgment()
        except Exception as err:
            log.error(err)

        log.info(
            ">>> [%s] Finalizando cientificação automática dos substitutos >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
