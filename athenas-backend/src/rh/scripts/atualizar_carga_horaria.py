from rh.models import HoursWorkContract, Servidor, CargaHoraria
from datetime import datetime

from rh.utils import is_active


def criar_carga_servidor(servidor, jornada):
    """
    Função que criar uma carga horária para o servidor
    Args:
        servidor (object): objeto do servidor.
        jornada (object): Objeto da jornada de trabalho.
    """
    if not existe_carga_horaria(servidor, jornada) and verifica_criacao_carga_horaria(
        jornada, servidor
    ):
        criar_carga_horaria(jornada, servidor)


def atualizar_carga_servidor(servidor_id):
    """
    Função que atualiza a carga horária para o servidor
    Args:
        servidor_id (int): id do servidor.
    """
    servidor = Servidor.objects.get(pk=servidor_id)
    dt_exercicio = servidor.data_exercicio
    for carga_horaria in servidor.cargahoraria_set.all():

        jornada = carga_horaria.jornada_trabalho
        if jornada:
            dt_inicio_jornada = jornada.date_start

            dt_inicio = (
                dt_inicio_jornada if dt_inicio_jornada > dt_exercicio else dt_exercicio
            )
            dt_fim = buscar_data_fim_carga(servidor, jornada)

            carga_horaria_ativa = CargaHoraria.objects.filter(
                servidor=servidor, data_inicio=dt_inicio, data_fim=dt_fim, active=True
            ).exists()

            if not carga_horaria_ativa:
                CargaHoraria.objects.filter(pk=carga_horaria.pk).update(
                    data_inicio=dt_inicio,
                    data_fim=dt_fim,
                    active=is_active(date_start=dt_inicio, date_end=dt_fim),
                )


def existe_carga_horaria(servidor, jornada):
    """
    Função que verifica se existe carga horária do servidor por jornada
    Args:
        servidor (object): objeto do servidor.
        jornada (object): Objeto da jornada de trabalho.
    Returns:
        bool: True ou False
    """
    return CargaHoraria.objects.filter(
        jornada_trabalho=jornada, servidor=servidor
    ).exists()


def verifica_criacao_carga_horaria(jornada, servidor):
    """
    Função que verifica se é para criar carga horária do servidor conforme a jornada
    Args:
        jornada (object): Objeto da jornada de trabalho.
        servidor (object): objeto do servidor.
    Returns:
        bool: True ou False
    """
    dt_exercicio = servidor.data_exercicio
    dt_desligamento = servidor.data_desligamento

    if jornada.date_end and dt_desligamento:
        return (jornada.date_end and jornada.date_end >= dt_exercicio) and (
            dt_desligamento and dt_desligamento > jornada.date_start
        )
    else:
        return (
            (jornada.date_end and jornada.date_end >= dt_exercicio)
            or (dt_desligamento and dt_desligamento > jornada.date_start)
            or (not dt_desligamento and not jornada.date_end)
        )


def criar_carga_horaria(jornada, servidor):
    dt_inicio_jornada = jornada.date_start
    dt_exercicio = servidor.data_exercicio

    dt_inicio = dt_inicio_jornada if dt_inicio_jornada > dt_exercicio else dt_exercicio
    dt_fim = buscar_data_fim_carga(servidor, jornada)

    params = {
        "jornada_trabalho": jornada,
        "servidor": servidor,
        "data_inicio": dt_inicio,
        "data_fim": dt_fim,
        "quantidade": (jornada.duration_hour * 5),
        "active": False if dt_fim and dt_fim < datetime.today().date() else True,
    }
    carga_horaria = CargaHoraria.objects.create(**params)
    return carga_horaria


def buscar_data_fim_carga(servidor, jornada):
    data_fim_carga = None
    dt_desligamento = servidor.data_desligamento
    dt_fim_jornanda = jornada.date_end

    if dt_desligamento and dt_fim_jornanda:
        if dt_desligamento < dt_fim_jornanda:
            data_fim_carga = dt_desligamento
        else:
            data_fim_carga = dt_fim_jornanda
    elif dt_desligamento and not dt_fim_jornanda:
        data_fim_carga = dt_desligamento
    elif not dt_desligamento and dt_fim_jornanda:
        data_fim_carga = dt_fim_jornanda

    return data_fim_carga
