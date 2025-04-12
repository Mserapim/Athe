# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user
from contrib.utils import getLogger

from rh.antiguidades.lista_antiguidades_membros_utils import ListaAntiguidades

log = getLogger(__name__)


class Command(BaseCommand):
    help = """Rotina para alterar o status dos cadastros de trabalho remoto para inativo
    quando o mesmo tiver como ativo e a data final seja maior que a data de hoje. """

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):

        self.set_user_to_job("job_atualizar_lista_antiguidades_membros")
        self.atualiza_lista_antiguidades_membros()

    def atualiza_lista_antiguidades_membros(self):
        lista_antiguidades = ListaAntiguidades()
        lista_antiguidades.atualizar_lista_antiguidades_membros(origem="Job")
