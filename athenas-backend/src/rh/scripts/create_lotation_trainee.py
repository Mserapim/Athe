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

    def _create_exercise(dec):

        try:
            sl = ServidorLotacao.objects.get(
                servidor=dec.servidor,
                designacao=True,
            )

            fields_update = {
                "designacao": False,
                "publicacao": (
                    dec.publicacao_movimentacao
                    if dec.publicacao_movimentacao
                    else dec.publicacao_alteracao
                ),
            }
            return sl._create_by_copy(sl, fields_update)
        except Exception as err:
            print(f"ERRO: {err} /// {servidor}")

    query = Servidor.objects.filter(type_by_possession__in=["EST"])
    serv = []
    for servidor in query:

        for dec in DeclaracaoAtividade.objects.filter(servidor=servidor):
            _create_exercise(dec)
            serv.append(dec.servidor.matricula)
    print(serv)


if __name__ == "__main__":
    run()
