# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from datetime import datetime
from contrib.middleware import set_current_user
from corregedoria.cnmp.models import Communication


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "--exec-actions",
            default=None,
            action="store_true",
            dest="exec_actions",
            help="""Executada o envio de informacoes dos membros com pendencia de envio.""",
        )

        parser.add_argument(
            "--user",
            dest="user",
            required=True,
            help="Usuário que sera utilizado para executar a ação",
        )

        parser.add_argument(
            "--max-send",
            dest="max_send",
            default=10,
            required=False,
            help="Quantidade de envios a serem realizados. Padrao(10 envios)",
        )

    def _exec_actions(self, user, max_send):
        print("Envio de informacoes ao SCMMP - {}".format(datetime.today()))
        set_current_user(user)

        commun = Communication.objects.filter(status=1)[0 : int(max_send)]
        print("Numero de informacoes a serem enviadas: {}".format(commun.count()))
        for c in commun:
            try:
                c.send()
            except Exception as e:
                print(str(e))

        print("Finalizando envio de informacoes pendentes ao SCMMP")

    def handle(self, exec_actions, user, max_send, *args, **kwargs):
        if exec_actions is True:
            self._exec_actions(user, max_send)
