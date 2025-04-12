# -*- coding: utf-8 -*-
import inspect

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import MovimentacaoSubstituicao
from standard.models import Item

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--afastamento",
            action="store_true",
            dest="afastamento",
            help="Atualiza estado dos afastamentos.",
        )

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def _get_datetime(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _print_arquimedes_error(self, error):
        msg = f"[{self._get_datetime()}] {str(error)}"
        log.warning(msg)
        print(msg)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        if options["afastamento"]:
            self.set_user_to_job("job_update_servidor_afastamento")
            self.afastamento()

    def afastamento(self):
        date_value = Item.objects.get(key="date_update_employee_retroactive").value
        date_retroactive = datetime.strptime(date_value, "%d/%m/%Y").date()
        BaseLicencaAfastamento.atualizar_estado(data=date_retroactive)
        self.atualizar_movimentacao_substituicao(date=date_retroactive)
        self.mark_exercise_departure()

    def atualizar_movimentacao_substituicao(self, date=None):
        log.info(
            "COMANDO -> atualizar_movimentacao_substituicao(MovimentacaoSubstituicao.call_update_responsible_workplace)"
        )
        MovimentacaoSubstituicao.call_update_responsible_workplace(date=date)
        MovimentacaoSubstituicao.cmd_replacement_manager(date=date)
        MovimentacaoSubstituicao.update_state(date=date)

    def mark_exercise_departure(self):
        BaseLicencaAfastamento.mark_exercise_departure()
