# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user, get_current_user
from contrib.utils import getLogger

from engine.mq.models import Task

from rh.registerpoint.models import MarkPoint

from rh.registerpoint.tasks_atualizar_campo_marcacao import (
    atualizar_campo_marcacao_task,
)


log = getLogger(__name__)


class Command(BaseCommand):
    help = """Script para popular o campo 'marcacao' do model MarkPoint, utilizando como dados a concatenação
    dos campos 'day' e 'mark' do mesmo modelo."""

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):

        self.set_user_to_job("job_folhaponto_atualizar_campo_marcacao")
        self.atualizar_campo_marcacao()

    def atualizar_campo_marcacao(self):
        log.info("Iniciando script para popular campo marcacao do model MarkPoint.")

        user = get_current_user()
        for marc in MarkPoint.objects.filter(marcacao__isnull=True):
            Task.start(
                atualizar_campo_marcacao_task,
                description=f"Atualização do campo marcacao do model MarkPoint.",
                user=user.id,
                marcacao_id=marc.pk,
            )
