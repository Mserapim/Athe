from datetime import datetime

from contrib.documents import mascarar_cpf

from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user
from engine.mq.models import Task

from rh.gfp.models import Servidor

from rh.servidor.tasks_atualizar_infos import atualizar_username_task


log = getLogger(__name__)


class AtualizarInfosServidor(object):
    """
    Classe com métodos e lógicas para para atualizar informações do Servidor
    """

    def __init__(self, *args, **kwargs):
        usuario = get_current_user()
        if usuario is None:
            set_current_user("athenas")

    def buscar_servidores(self):
        q_servidores = Servidor.objects.filter(verificado_mastiff=False)

        return [servidor for servidor in q_servidores if servidor.is_ativo()]

    def atualizar_username(self, servidor):
        cpf_mascarado = mascarar_cpf(servidor.pessoa_fisica.cpf)

        log.info(
            f">>> [{datetime.now()}] Iniciando atualização de username do Servidor: {servidor}."
        )

        try:
            Task.start(
                atualizar_username_task,
                description=f"Processamento para sincronizar CPFs à nomeação de residente.",
                user=get_current_user().pk,
                servidor_id=servidor.pk,
                cpf_mascarado=cpf_mascarado,
            )
        except Exception as e:
            log.info(
                f">>> [{datetime.now()}] Erro na atualização de username do Servidor: {servidor}"
            )
            log.error(e)

        log.info(
            f">>> [{datetime.now()}] Atualização de username do Servidor: {servidor} concluída."
        )

    def atualizar_username_todos_servidores(self):
        servidores = self.buscar_servidores()
        log.info(
            f">>> Quantidade de Servidores para serem consultados e atualizados: {len(servidores)}."
        )

        [self.atualizar_username(servidor) for servidor in servidores]
