from contrib.middleware import get_current_user
from rh.models import ServidorLotacao

from contrib.utils import getLogger

log = getLogger(__name__)


def get_lotacao_atual(servidor):
    """Retorna a lotação do atual servidor"""
    servidor_lotacao = ServidorLotacao.objects.filter(
        servidor__matricula=servidor.matricula, designacao=False, ativo=True
    )
    if servidor_lotacao:
        lotacao = servidor_lotacao.first().lotacao
        return lotacao
    else:
        raise Exception("Não foi possível encontrar a lotação do servidor.")


def get_lotacao_superior(servidor):
    """
    Busca a lotação atual do servidor ou lotação superior se for responsável pela lotação atual
    """
    servidor_lotacao = ServidorLotacao.objects.filter(
        servidor__matricula=servidor.matricula, designacao=False, ativo=True
    )
    if servidor_lotacao:
        lotacao_superior = servidor_lotacao.first().lotacao
        if lotacao_superior.responsavel == servidor:
            return lotacao_superior.pai
        return lotacao_superior
    else:
        raise Exception("Não foi possível encontrar a lotação do servidor.")


def get_aprovador(servidor):
    """
    Método que retorna o aprovador da solicitação de servidores.
    Args:
    - servidor
    Returns:
        Aprovador(Servidor).
    """
    if servidor.type_by_possession in [
        "EFE",
        "ECM",
        "CMS",
        "REQ",
        "RCM",
        "EFC",
        "REX",
        "EXT",
    ]:
        lotacao_atual = get_lotacao_atual(servidor)
        lotacao_superior = get_lotacao_superior(servidor)

        if (
            servidor.chefe_imediato
            and lotacao_atual.responsavel != servidor.chefe_imediato
        ):
            if servidor.chefe_imediato.afastamento_ativo():
                if servidor.chefe_imediato.substitutions():
                    return servidor.chefe_imediato.substitutions().first().servidor
                else:
                    return servidor.chefe_imediato
            else:
                return servidor.chefe_imediato
        else:
            resposavel_lotacao = None
            while not resposavel_lotacao:
                if (
                    lotacao_superior.responsavel
                    and lotacao_superior.portal_approver
                    and lotacao_superior.responsavel != servidor
                ):
                    resposavel_lotacao = lotacao_superior.responsavel
                else:
                    if lotacao_superior.pai:
                        lotacao_pai = lotacao_superior.pai
                        lotacao_superior = lotacao_pai
                    else:
                        break

            if not resposavel_lotacao:
                raise Exception(
                    "Não foi possível encontrar um aprovador. Entre em contato com o DGP."
                )

            if resposavel_lotacao.afastamento_ativo():
                if resposavel_lotacao.substitutions():
                    return resposavel_lotacao.substitutions().first().servidor
                else:
                    return resposavel_lotacao
            else:
                return resposavel_lotacao
    else:
        resposavel_lotacao = None
