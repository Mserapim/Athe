# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import Servidor

log = getLogger(__name__)


class Command(BaseCommand):
    help = "Remove servidores inativos dos grupos de usuários."

    def set_user_to_job(self, username: str) -> None:
        """
        Define o usuário para o trabalho com base no nome de usuário.
        Se o usuário não for encontrado, define 'athenas' como o usuário atual.

        :param username: Nome de usuário a ser configurado.
        """
        try:
            user = User.objects.get(username=username)
            set_current_user(user)
        except User.DoesNotExist:
            log.error(
                f'Usuário "{username}" não encontrado. Definindo usuário "athenas".'
            )
            user = User.objects.get(username="athenas")
            set_current_user(user)

    def handle(self, *args, **options):
        """
        Manipula o comando de limpeza de grupos de usuários para servidores inativos.
        """
        self.set_user_to_job("job_limpar_grupo_usuarios_servidores_inativos")
        self.limpar_grupo_usuarios_servidores_inativos()

    def limpar_grupo_usuarios_servidores_inativos(self):
        """
        Remove servidores inativos dos grupos de usuários.
        """
        log.info(
            "COMANDO -> limpar_grupo_usuarios_servidores_inativos. Removendo servidores inativos dos grupos de usuários."
        )

        servidores = Servidor.objects.filter(
            ativo=False, grupos_permissao__isnull=False
        )

        for servidor in servidores:
            servidor.grupos_permissao.clear()
            log.info(f"Servidor {servidor.id} removido dos grupos de permissão.")
