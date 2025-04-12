# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from datetime import date

from rh.models import MembersTelecommuting


log = getLogger(__name__)


class Command(BaseCommand):
    help = """Rotina que faz a verificação e atualização dos status de trabalho remoto:
1. Altera o status para "AGENDADO" para aqueles registros cuja data de início é posterior à data atual.
2. Modifica o status para "INATIVO" nos registros que estão marcados como "ATIVO" e cuja data final é anterior à data atual.
3. Atualiza o status para "ATIVO" em registros que estão com status "AGENDADO" e cuja data de início é igual à data de hoje."""

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):

        self.set_user_to_job("job_automacao_status_trabalho_remoto")
        self.aut_status_trab_remoto()

    def aut_status_trab_remoto(self):
        log.info(
            "Iniciando rotina para conferir e alterar os status dos trabalhos remotos."
        )
        hoje = date.today()
        log.info("Selecionando registros cuja data_inicio é maior que hoje")

        q_membros_agendado = MembersTelecommuting.objects.filter(data_inicio__gt=hoje)
        if q_membros_agendado.exists():
            log.info("Alterando o status dos registros para AGENDADO.")
            q_membros_agendado.update(status=3)

        log.info(
            "Selecionando registros com status ATIVO cuja data_fim é menor que hoje"
        )
        q_membros_inativos = MembersTelecommuting.objects.filter(
            status=1, data_fim__lt=hoje
        )
        if q_membros_inativos.exists():
            log.info("Alterando o status dos registros que venceram para INATIVO.")
            q_membros_inativos.update(status=2)
        else:
            log.info("Nenhum registro ATIVO vencido encontrado.")

        log.info(
            "Selecionando registros com status AGENDADO cuja data_inicio é igual a hoje"
        )
        q_membros_ativos = MembersTelecommuting.objects.filter(
            status=3, data_inicio=hoje
        )
        if q_membros_ativos.exists():
            log.info("Alterando o status dos registros AGENDADOS para ATIVO.")
            q_membros_ativos.update(status=1)
        else:
            log.info("Nenhum registro AGENDADO para se tornar ATIVO encontrado.")
