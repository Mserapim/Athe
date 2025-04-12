from common.util.api.waitingwork import reg_waiting_work
from contrib.utils import employee_from_user
from contrib.middleware import get_current_user


@reg_waiting_work("epadm_inbox")
def epadm_inbox_unread():
    from edocs.processo.api import EDOCBoxQueryProcesso

    count = 0

    try:
        employee = employee_from_user(get_current_user())
        work_locations = employee.work_locations_effective_exercise

        query = EDOCBoxQueryProcesso(
            servidor=employee,
            lotacoes=work_locations,
            lotacoes_protocolo_geral=[
                lotacao.pk
                for lotacao in work_locations
                if lotacao.acesso_protocolo_geral
            ],
        )

        query = query.get_caixa_entrada().exclude(
            EDOCBoxQueryProcesso.get_finalizado_recebido()
        )

        query = query.filter(
            protocolo__processo__isnull=False, data_recebimento=None
        ).order_by("-data_encaminhamento")

        count = query.count()

    except AttributeError:
        count = 0

    return {
        "title": "E-PADM a receber",
        "count": count,
        "type": "documentos" if count > 1 else "documento",
        "controller": "EpadProcesso",
    }
