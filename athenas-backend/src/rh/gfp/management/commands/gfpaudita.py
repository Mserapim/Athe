# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db.models import Q

from rh.gfp.calculo_auditoria import Auditoria
from rh.gfp.models import Folha


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "-m", "--mes", help="Indica o mes da folha.", dest="mes", default=None
        )
        parser.add_argument(
            "-a", "--ano", help="Indica o ano da folha.", dest="ano", default=None
        )
        parser.add_argument(
            "-t", "--tipo", help="Id ou nome da folha.", dest="tipo", default=None
        )
        parser.add_argument(
            "-e",
            "--eventos",
            help='Eventos a serem auditados "N1,N2,...,Nn.',
            dest="eventos",
            default=None,
        )

    def handle(self, mes=None, ano=None, tipo=None, eventos=None, **kargs):
        folha = None

        try:
            folha = Folha.objects.get(
                Q(Q(tipo_folha__titulo=tipo) | Q(tipo_folha__abreviatura=tipo)),
                periodo__mes=mes,
                periodo__ano=ano,
            )
        except Folha.DoesNotExist:
            print("Não consegui encontra a folha desejada.")
        else:
            if eventos is not None:
                eventos = eventos.split(",")
            Auditoria(folha=folha.pk, eventos=eventos).audita()
