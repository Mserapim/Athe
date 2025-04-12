from contrib.utils import getLogger
from rh.afastamento.models import CANCELADO


log = getLogger(__name__)


def validar_substituto_afastamento(servidor):
    if servidor.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
        from datetime import datetime
        from rh.afastamento.models import BaseLicencaAfastamento

        hoje = datetime.now().date()
        query = BaseLicencaAfastamento.objects.filter(
            servidor=servidor, data_inicio__lte=hoje, data_fim__gte=hoje
        ).exclude(estado=CANCELADO)
        if query.exists() and query.first().substituicao.exists():
            return True
    return False
