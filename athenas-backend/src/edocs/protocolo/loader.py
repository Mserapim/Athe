# -*- coding:utf-8 -*-
from django.db.models import Q
from common.util.api.waitingwork import reg_waiting_work


@reg_waiting_work("edoc_inbox")
def edoc_inbox_unread():
    from edocs.protocolo.models import Movimentacao

    query = Q(
        Q(data_recebimento=None),
        Q(with_workflow=False),
        Q(protocolo__processo__isnull=True),
    )

    count = 0

    try:
        count = Movimentacao.inbox_queryset().filter(query).count()

    except AttributeError:
        count = 0

    return {
        "title": "E-Doc a receber",
        "count": count,
        "type": "documentos" if count > 1 else "documento",
        "controller": "EDOCManage",
    }
