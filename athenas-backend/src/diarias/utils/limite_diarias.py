from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Q

from contrib.utils import getLogger
from diarias.models import Beneficiario, LimiteDiarias, Viagem
from standard.models import Choice

log = getLogger()


def buscar_limite_uso(servidor, ano=None, lista_meses=None):
    """
    Busca os limites de uso de diárias de um servidor para um determinado ano e lista de meses.

    Args:
        servidor.
        ano (int, optional): Ano para o qual os limites de uso serão buscados. Se não fornecido, usa o ano atual.
        lista_meses (list of int, optional): Lista de meses (1-12) para os quais os limites de uso serão buscados. Se não fornecido, usa todos os meses do ano.

    Returns:
        dict: Um dicionário contendo os limites de uso de diárias organizados por tipo (mensal e anual) e os respectivos usos.
    """

    ano = int(ano) if ano else date.today().year
    meses = list(map(int, lista_meses)) if lista_meses else range(1, 13)

    tipo = "membro" if servidor.tipo == "M" else "servidor"
    limites = LimiteDiarias.objects.filter(tipo=tipo)

    if len(limites) == 1 and limites[0].referencia == "mensal":
        meses = range(1, 13)

    rascunho = 2  # ID do fluxo Solicitante - Rascunho
    indeferido = 32  # ID do fluxo Indeferido - Cancelado
    cancelado = 21  # ID do fluxo Beneficiário - Cancelado
    filtro_data = Q(data_inicio_viagem__year=ano) | Q(data_fim_viagem__year=ano)
    viagens_ano = Viagem.objects.filter(
        filtro_data, beneficiarios__servidor=servidor
    ).exclude(beneficiarios__fluxo__id__in=[rascunho, cancelado, indeferido])

    resultados = {
        "tipo": tipo,
        "ano": ano,
        "mensal": {f"{m:02d}": {} for m in meses},
        "anual": {},
    }

    for limite in limites:
        chave = ",".join(map(str, sorted(limite.motivos_viagem)))
        choices = Choice.objects.filter(
            app_label="diarias", name="MOTIVO_VIAGEM", value__in=limite.motivos_viagem
        ).order_by("value")
        labels = ", ".join([choice.label for choice in choices])

        if limite.referencia == "mensal":
            for m in meses:
                resultados["mensal"][f"{m:02d}"][chave] = {
                    "motivos": labels,
                    "limite": "Ilimitado" if limite.limite is None else limite.limite,
                    "uso": 0,
                    "saldo": "Ilimitado" if limite.limite is None else limite.limite,
                }
        elif limite.referencia == "anual":
            resultados["anual"][chave] = {
                "motivos": labels,
                "limite": "Ilimitado" if limite.limite is None else limite.limite,
                "uso": 0,
                "saldo": "Ilimitado" if limite.limite is None else limite.limite,
            }

    for mes in meses:
        viagens_mes = viagens_ano.filter(
            Q(data_inicio_viagem__month=mes) | Q(data_fim_viagem__month=mes)
        )
        calcular_uso(servidor, viagens_mes, resultados["mensal"], ano, [mes])

    calcular_uso(servidor, viagens_ano, resultados["anual"], ano)

    return resultados


def calcular_uso(servidor, viagens, resultado, ano, meses=None):
    """
    Calcula os dias de uso de diárias para as viagens fornecidas e atualiza o resultado.
    """
    if meses is None:
        meses = []

    for viagem in viagens:
        beneficiario = Beneficiario.objects.filter(
            viagem=viagem, servidor=servidor
        ).first()
        calculo_consolidado = getattr(
            beneficiario, "calculos_diarias_consolidados", None
        )

        if (
            calculo_consolidado
            and calculo_consolidado.qtd_total_diarias_deferido is not None
        ):
            qtd_diarias = Decimal(calculo_consolidado.qtd_total_diarias_deferido)
        else:
            if calculo_consolidado:
                qtd_diarias = Decimal(calculo_consolidado.qtd_total_diarias)
            else:
                qtd_diarias = Decimal(0)

        motivo_viagem = str(viagem.motivo_viagem)
        data_inicio_viagem = viagem.data_inicio_viagem

        for mes in meses:
            if mes == data_inicio_viagem.month:
                ultimo_dia_mes = (
                    data_inicio_viagem.replace(day=28) + timedelta(days=4)
                ).replace(day=1) - timedelta(days=1)
                dias_restantes_no_mes = (ultimo_dia_mes - data_inicio_viagem).days + 1

                if qtd_diarias <= dias_restantes_no_mes:
                    mes_viagem = f"{data_inicio_viagem.month:02d}"
                    atualizar_resultado(
                        mes_viagem, motivo_viagem, qtd_diarias, resultado, meses
                    )
                else:
                    mes_viagem = f"{data_inicio_viagem.month:02d}"
                    atualizar_resultado(
                        mes_viagem,
                        motivo_viagem,
                        dias_restantes_no_mes,
                        resultado,
                        meses,
                    )

            elif mes == (data_inicio_viagem + timedelta(days=30)).month:
                ultimo_dia_mes = (
                    data_inicio_viagem.replace(day=28) + timedelta(days=4)
                ).replace(day=1) - timedelta(days=1)
                dias_restantes_no_mes = (ultimo_dia_mes - data_inicio_viagem).days + 1

                if qtd_diarias > dias_restantes_no_mes:
                    dias_no_proximo_mes = qtd_diarias - dias_restantes_no_mes
                    mes_proximo = f"{mes:02d}"
                    atualizar_resultado(
                        mes_proximo,
                        motivo_viagem,
                        dias_no_proximo_mes,
                        resultado,
                        meses,
                    )


def atualizar_resultado(mes_destino, motivo_viagem, qtd_diarias, resultado, meses):
    """
    Atualiza o uso e saldo de diárias no resultado, seja ele mensal ou anual.

    Args:
        mes_destino (str): Mês a ser atualizado.
        motivo_viagem (str): Motivo da viagem.
        qtd_diarias (Decimal): Quantidade de diárias a ser somada.
        resultado (dict): Dicionário que contém os resultados a serem atualizados.
        meses (list): Lista de meses para o cálculo mensal.
    """
    # Atualiza os resultados mensais
    if meses:
        if mes_destino in resultado:
            for motivos, dados in resultado[mes_destino].items():
                if motivo_viagem in motivos.split(","):
                    dados["uso"] += qtd_diarias
                    if dados["limite"] != "Ilimitado":
                        dados["saldo"] = dados["limite"] - dados["uso"]
    else:
        # Atualiza os resultados anuais
        for motivos, dados in resultado.items():
            if motivo_viagem in motivos.split(","):
                dados["uso"] += qtd_diarias
                if dados["limite"] != "Ilimitado":
                    dados["saldo"] = dados["limite"] - dados["uso"]
