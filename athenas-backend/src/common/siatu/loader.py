# -*- coding:utf-8 -*-

from contrib.middleware import get_current_user
from django.db.models import Q
from common.util.api.waitingwork import reg_waiting_work


@reg_waiting_work("siatu_waiting_valuation")
def siatu_waiting_valuation():
    from common.siatu.models import Chamado, Status

    query = Q(
        Q(solicitacao__solicitante=get_current_user()),
        Q(status_atual__status=Status.AGUARDANDO_AVALIACAO),
    )

    count = 0

    try:
        count = Chamado.objects.filter(query).count()

    except AttributeError:
        count = 0

    return {
        "title": "SIATU aguardando avaliação",
        "count": count,
        "type": "chamados" if count > 1 else "chamado",
        "controller": "SiatuChamadoSolicitante",
    }
