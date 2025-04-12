# -*- coding: utf-8 -*-

from importlib import import_module

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from rh.gfp.models import Evento, Folha


class Command(BaseCommand):
    verbose = "False"
    help = """Loader dos arquivos enviados para processamento na folha de pagamento."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-l",
            "--loader",
            help="Loader para ser utilizado para realizar a carga do arquivo.",
            dest="loader",
        ),
        parser.add_argument(
            "-f",
            "--folha",
            help="Id da folha de pagamento que deseja incluir os eventos.",
            dest="folha_id",
        ),
        parser.add_argument(
            "--fonte", help="Arquivo onde estão os eventos.", dest="fonte"
        ),
        parser.add_argument(
            "--evento",
            help="Número do evento a ser utilizado.",
            dest="evento",
            default=None,
        )

    def factoryLoader(self, loader, fonte, folha, evento=None):
        path_path = loader.split(".")
        loader_name = path_path[-1]
        module = ".".join(path_path[:-1])

        mod = import_module(module)
        Loader = getattr(mod, loader_name)

        if evento is None:
            return Loader(fonte, folha=folha)
        else:
            return Loader(fonte, folha=folha, evento=evento)

    def handle(self, loader, fonte, folha_id, evento=None, **options):
        set_current_user(User.objects.get(username="athenas"))

        if evento is not None:
            evento = Evento.objects.get(numero=evento)

        self.factoryLoader(
            loader, fonte, Folha.objects.get(pk=folha_id), evento=evento
        ).execute()
