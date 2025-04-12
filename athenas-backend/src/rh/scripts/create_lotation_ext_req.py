import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import (
    BKP_MovimentacaoPosseReq,
    DeclaracaoAtividade,
    EncargoFinanceiro,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    MovimentacaoRequisicao,
    PeriodoRequisicao,
    PossessionCollaborator,
    RequestMove,
    Servidor,
    ServidorLotacao,
)


log = getLogger(__name__)


set_current_user("athenas")


def run():
    print(
        """

        Este script cria um ServidorLotacao para os servidores migrados do Declaracao de Atividade.

    """
    )

    def _create_exercise(declaracao_atividade):
        if declaracao_atividade:

            defaults = {
                "publicacao": (
                    declaracao_atividade.publicacao_movimentacao
                    if declaracao_atividade.publicacao_movimentacao
                    else declaracao_atividade.publicacao_alteracao
                ),
                "data_vigencia": declaracao_atividade.data_exercicio,
                "data_vigencia_fim": declaracao_atividade.data_encerramento,
                "provisorio": True,
            }
            try:
                sl, created = ServidorLotacao.objects.get_or_create(
                    publicacao=declaracao_atividade.publicacao_movimentacao,
                    servidor=declaracao_atividade.servidor,
                    lotacao=declaracao_atividade.lotacao,
                    data_vigencia_inicio=declaracao_atividade.data_exercicio,
                    defaults=defaults,
                )
                if sl:
                    sl.create_work_assignment()
                    print(sl.servidor)
                else:
                    print(
                        f"ERRO: {declaracao_atividade.servidor} - Lotacao: {declaracao_atividade.lotacao}"
                    )
            except Exception as err:
                print(
                    f"ERRO: {err} /// {declaracao_atividade.servidor} - Lotacao: {declaracao_atividade.lotacao}"
                )

    query = Servidor.objects.filter(type_by_possession__in=["EXT", "REQ"])
    serv = []
    for servidor in query:

        for dec in DeclaracaoAtividade.objects.filter(servidor=servidor):
            _create_exercise(dec)
            serv.append(dec.servidor.matricula)
    print(serv)


if __name__ == "__main__":
    run()
