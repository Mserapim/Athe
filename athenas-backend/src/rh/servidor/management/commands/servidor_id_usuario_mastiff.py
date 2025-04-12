# -*- coding: utf-8 -*-

from datetime import datetime
from django.core.management.base import BaseCommand
from contrib.documents import mascarar_cpf
from engine.mq.models import Task
from rh.models import Servidor
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import getLogger
from rh.servidor.tasks_servidor_id_usuario_mastiff import (
    atualizar_id_usuario_mastiff_task,
)


log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando faz a atualização do id_usuario_mastiff dos Servidores do Athenas."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--todos",
            action="store_true",
            dest="atualizar_id_usuario_mastiff",
            help="Atualização do campo id_usuario_mastiff",
        )

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        if options["atualizar_id_usuario_mastiff"]:
            self.atualizar_id_usuario_mastiff_servidores()

    def atualizar_id_usuario_mastiff_servidores(self):
        set_current_user(get_current_user())

        log.info(
            f">>> [{datetime.now()}] Iniciando atualização do id_usuario_mastiff dos Servidores."
        )
        try:
            servidores = Servidor.objects.filter(
                ativo=True, id_usuario_mastiff__isnull=True
            ).exclude(type_by_possession__in=["BFP", "SAP", "COE", "MAP"])
            for servidor in servidores:
                cpf_mascarado = mascarar_cpf(servidor.pessoa_fisica.cpf)
                Task.start(
                    atualizar_id_usuario_mastiff_task,
                    description=f"Processamento para atualizar o id_usuario_mastiff.",
                    user=get_current_user().pk,
                    servidor_id=servidor.pk,
                    cpf_mascarado=cpf_mascarado,
                )
        except Exception as e:
            log.info(
                f">>> [{datetime.now()}] Erro na atualização do id_usuario_mastiff dos Servidores"
            )
            log.error(e)

        log.info(
            f">>> [{datetime.now()}] Atualização id_usuario_mastiff dos Servidores concluída."
        )
