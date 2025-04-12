# -*- coding: utf-8 -*-
from common.util.api.waitingwork import reg_waiting_work
from contrib.middleware import get_current_user
from django.db.models import Q
from datetime import datetime


@reg_waiting_work("agreement_near_due_date")
def agreement_near_due_date():
    from planejamento.contrato.models import Contrato

    count = 0

    try:
        user = get_current_user()

        if hasattr(user, "servidor"):
            query = Q(Q(agreementsupervisors__employee__user=user), Q(status=0))

            for c in Contrato.objects.filter(query):
                if c.pending() not in (0, 2):
                    count = count + 1

    except AttributeError:
        count = 0

    return {
        "title": "Contrato próximo do vencimento",
        "count": count,
        "type": "contratos" if count > 1 else "contrato",
        "controller": "PHAAgreement",
    }


@reg_waiting_work("agreement_due_date")
def agreement_due_date():
    from planejamento.contrato.models import Contrato

    count = 0

    try:
        user = get_current_user()

        if hasattr(user, "servidor"):
            query = Q(
                Q(agreementsupervisors__employee__user=user),
                Q(status=0),
                Q(data_vencimento_flag__lte=datetime.now().date()),
            )

            count = Contrato.objects.filter(query).count()

    except AttributeError:
        count = 0

    return {
        "title": "Contrato com prazo vencido",
        "count": count,
        "type": "contratos" if count > 1 else "contrato",
        "controller": "PHAAgreement",
    }
