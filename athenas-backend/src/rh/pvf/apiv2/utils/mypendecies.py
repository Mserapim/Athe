from rh.pvf.apiv2.utils.approval import (
    filtro_tipo_servidor,
    group_list,
    query_approvals,
)
from rh.pvf.minhaspendencias import MinhasPendencias
from datetime import datetime
from rh.registerpoint.models import MarkPoint
from rh.pvf.apiv2.utils.telework import is_workplan
from django.db.models.query_utils import Q


def my_pendecies_data(employee):
    """
    Retorna uma lista de informações de pendências relacionadas a um servidor.
    args:
        employee (objeto): O objeto que representa um servidor.
    returns:
        list: Uma lista contendo as informações de pendências do servidor.
    """
    minhas_pendencias = MinhasPendencias()
    data = minhas_pendencias.pendencias(employee)
    return data
