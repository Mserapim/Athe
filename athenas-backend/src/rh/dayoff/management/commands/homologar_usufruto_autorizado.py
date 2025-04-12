# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.dayoff.const import ACT_SELL, USU_AUTORIZED_CI, USU_ENJOYED
from rh.dayoff.models import Activity


log = getLogger("db")


class Command(BaseCommand):
    help = """Script para homologar as atividades e usufrutos do gerenciador admin 
    de plantão eleitoral com status de autorizado e criar seu respectivo afastamento)"""

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("job_homologar_usufrutos_autorizado")
        self.homologar_usufrutos_autorizado()

    def homologar_usufrutos_autorizado(self):
        atividades = Activity.objects.filter(
            status=ACT_SELL, usufructs__status__in=[USU_AUTORIZED_CI, USU_ENJOYED]
        )
        for atividade in atividades:
            try:
                atividade = atividade.my_origin
                atividade.homologate(homologate=True, context="admin")
                log.info(
                    f"Atualizando status de {atividade.usufructsin} - {atividade.status}"
                )
            except Exception as err:
                log.error(err)
