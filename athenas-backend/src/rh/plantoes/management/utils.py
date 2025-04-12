from contrib.daterange import NewDateRange
from datetime import datetime
import requests
from django.conf import settings


def get_api_plantoes_membros(dt_inicio, dt_fim):
    """
    Retorna os plantões realizando pelos membros.
    :returns: list
    """
    data = {
        "data_inicio": dt_inicio.strftime("%Y-%m-%d"),
        "data_fim": dt_fim.strftime("%Y-%m-%d"),
    }

    headers = {
        "Authorization": f"Bearer {settings.TOKEN_API_PLANTOES}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{settings.PLANTOES_API_URL}/por_periodo", headers=headers, json=data
    )
    return response.json()


def dias_plantoes(de, ate) -> tuple:
    """
    Retorna a quantidade de dias de plantoes no range de período do plantão.
    :returns: (tuple) [0] (int) Dias de plantões |
                          [1] (list) lista de dates
    """
    if not de or not ate:
        raise Exception("NewDateRange não informado.")
    else:
        dt_inicio = datetime.strptime(de, "%Y-%m-%d").date()
        dt_fim = datetime.strptime(ate, "%Y-%m-%d").date()
        intervalo_data = NewDateRange(dt_inicio, dt_fim)
        dias = 0
        lista_data = []

        for data in intervalo_data.iter():
            dias += 1
            lista_data.append(data)
        d_plantoes = dias
        return d_plantoes, lista_data
