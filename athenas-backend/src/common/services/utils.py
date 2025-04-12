import os

from datetime import datetime
from contrib.middleware import get_current_user
from django.conf import settings

from common.services.models import HistoricoServico, ScheduledServices
from common.services.scripts.create_job_users import JOB_USERS

from contrib.utils import getLogger


log = getLogger(__name__)


def atualiza_info_execucao_servico(servico, executado):
    """
    Esta função atualiza o serviço com as informações da execução atual.
    """
    ScheduledServices.objects.filter(id=servico.id).update(
        executado_por=get_current_user(),
        executado_em=datetime.today(),
        executado=executado,
        em_execucao=False,
    )


def tmp_dir():
    return os.path.join(settings.UPLOAD_STORE_DIR, "service")


def gerar_historico_servico(servico, inicio):
    """
    Esta função gera um histórico de serviço com as informações da execução atual.
    """
    user = get_current_user()
    if user.username in JOB_USERS:
        execucao = 2  # Automático
    else:
        execucao = 1  # Manual

    historico = HistoricoServico.objects.create(
        iniciado_em=inicio,
        servico=servico,
        execucao=execucao,
    )

    return historico


def atualizar_historico_servico(historico_servico, sucesso, fim):
    """
    Esta função atualiza um histórico de serviço com as informações da execução atual.
    """
    historico_servico.finalizado_em = fim
    # historico_servico.ssid = uuid
    historico_servico.sucesso = sucesso
    historico_servico.save()
