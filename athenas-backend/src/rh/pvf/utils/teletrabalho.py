import calendar
from datetime import date
from django.db.models.query_utils import Q
from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais
from rh.models import MovimentacaoTeletrabalho


def get_teletrabalhos_semestrais(servidor):
    """
    Função que retorna os planos onde servidor foi aprovador no semestre
    args:
        servidor (objeto): instancia do servidor.
    returns:
        list: lista de planos onde o servidor foi aprovador no semestre.
    """
    data_atual = date.today()
    periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.last()
    if periodo:
        data_inicio_envio = periodo.data_inicio_periodo_envio
        data_fim_envio = periodo.data_fim_periodo_envio

        if data_inicio_envio <= data_atual <= data_fim_envio:
            mes_inicio_analisado, ano_inicio_analisado = map(
                int, periodo.data_inicio_periodo_analisado.split("/")
            )
            mes_fim_analisado, ano_fim_analisado = map(
                int, periodo.data_fim_periodo_analisado.split("/")
            )
            data_inicio_analisado = date(ano_inicio_analisado, mes_inicio_analisado, 1)
            ultimo_dia_mes_fim_analisado = calendar.monthrange(
                ano_fim_analisado, mes_fim_analisado
            )[1]
            data_fim_analisado = date(
                ano_fim_analisado, mes_fim_analisado, ultimo_dia_mes_fim_analisado
            )

            mov_teletrabalhos = MovimentacaoTeletrabalho.objects.filter(
                Q(aprovador=servidor)
                & (
                    Q(data_inicio__lte=data_fim_analisado)
                    & Q(data_fim__gte=data_inicio_analisado)
                )
            )
            return mov_teletrabalhos
    return []
