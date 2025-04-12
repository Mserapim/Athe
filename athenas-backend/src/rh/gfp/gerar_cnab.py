from django.db.models import Count, Sum

from rh.gfp.models import FolhaEvento
from adm.cnab_gerador.cnab_240.bb_cnab_240_gerar_pgto import BBCnab240GerarPgto
import re

from standard.models import Item


def consolidar_infos_beneficiario_cnab(*args, **kwargs):
    """
    Método responsável por normalizar os dados do favorecido
    """

    return {
        "doc": kwargs.get("doc"),
        "tipo_doc": kwargs.get("tipo_doc"),  # tipo de inscrição - CPF = '1', CNPJ = '2'
        "nome": kwargs.get("nome"),
        "cod_banco": kwargs.get("cod_banco"),
        "agencia_num": kwargs.get("agencia_num"),
        "agencia_dv": kwargs.get("agencia_dv"),
        "conta_num": kwargs.get("conta_num"),
        "conta_dv": kwargs.get("conta_dv"),
        "tipo_conta": kwargs.get(
            "tipo_conta"
        ),  # tipo de conta - '1' = conta corrente, '2' - conta poupança
        "valor_pgto": kwargs.get("valor_pgto"),
    }


def consolidar_infos_beneficiario_cnab_pensionista(evento_pen):
    pensionista = evento_pen.contracheque.pensioner
    dados_bancario = evento_pen.contracheque.dado_bancario_pessoa

    agencia = re.sub(r"(\.|-)", "", dados_bancario.agencia)
    agencia_num = agencia[0:-1]
    agencia_dv = agencia[-1].upper()

    conta_completa = re.sub(r"(\.|-)", "", dados_bancario.conta_corrente_completa)
    conta_num = conta_completa[0:-1]
    conta_dv = "0" if dados_bancario.tipo_conta == "2" else conta_completa[-1].upper()

    return {
        "doc": pensionista.cpf,
        "tipo_doc": "1",  # tipo de inscrição - CPF = '1
        "nome": pensionista.social_name,
        "cod_banco": dados_bancario.banco.numero,
        "agencia_num": agencia_num,
        "agencia_dv": agencia_dv,
        "conta_num": conta_num,
        "conta_dv": conta_dv,
        "tipo_conta": dados_bancario.tipo_conta,
        "valor_pgto": evento_pen.correct_value,
    }


def gerar_cnab_pensionistas(folha, servidores):
    """
    Método responsável por criar a lógica de consolidação de valores de pensionistas e gerar o arquivo CNAB.
    """

    evento_ids = Item.objects.get(key="verba_pensionista_cnab").value.split(",")

    query_evento_pen = FolhaEvento.objects.filter(
        folha=folha, evento__pk__in=evento_ids
    )

    if servidores:
        query_evento_pen = query_evento_pen.filter(
            contracheque__servidor__pk__in=servidores
        )

    favorecidos_bb = []
    favorecidos_outros = []

    data_pgto = folha.dt_pagamento

    eventos_pgtos_bb = query_evento_pen.filter(
        contracheque__dado_bancario_pessoa__banco__numero="001"
    )
    favorecidos_bb = [
        consolidar_infos_beneficiario_cnab_pensionista(evento_pgto)
        for evento_pgto in eventos_pgtos_bb
    ]

    eventos_pgtos_outros = query_evento_pen.exclude(
        contracheque__dado_bancario_pessoa__banco__numero="001"
    )
    favorecidos_outros = [
        consolidar_infos_beneficiario_cnab_pensionista(evento_pgto)
        for evento_pgto in eventos_pgtos_outros
    ]

    arquivo_cnab = BBCnab240GerarPgto(
        tipo_servico="pgtos_diversos"
    ).criar_cnab_pgto_bb_outros_bancos(
        favorecidos_bb=favorecidos_bb,
        favorecidos_outros=favorecidos_outros,
        data_pgto=data_pgto,
    )

    return arquivo_cnab


def gerar_cnab_consignados(periodo_ano, periodo_mes, data_pgto):
    """
    Método responsável por criar a lógica de consolidação de valores de consignados e gerar o arquivo CNAB.

    params:
    pariodo_ano - int - Ano do período no formato AAAA
    pariodo_mes - int - Mês do período no formato MM
    data_pgto - date - Data do pagamento
    """
    config_carater = Item.objects.get(key="carater_verba_cnab_consignados").value
    verbas_carater = list(map(int, config_carater.split()))

    q_fe = (
        FolhaEvento.objects.filter(
            folha__periodo__ano=periodo_ano,
            folha__periodo__mes=periodo_mes,
            evento__banco_consignacao__isnull=False,
        )
        .filter(
            evento__carater__in=verbas_carater  # Caráter da verba (do evento) deve ser
        )
        .values(
            "evento__banco_consignacao__pessoajuridica__razao_social",
            "evento__banco_consignacao__pessoajuridica__cnpj",
            "evento__banco_consignacao__numero",
            "evento__banco_consignacao__agencia",
            "evento__banco_consignacao__dv_agencia",
            "evento__banco_consignacao__conta",
            "evento__banco_consignacao__dv_conta",
        )
        .annotate(
            Count("evento__banco_consignacao__numero"), total=Sum("correct_value")
        )
        .order_by("evento__banco_consignacao__numero")
    )

    favorecidos_bb = []
    favorecidos_outros = []

    for pgto in q_fe:
        conta_dv = pgto["evento__banco_consignacao__dv_conta"]
        agencia_dv = pgto["evento__banco_consignacao__dv_agencia"]
        params = {
            "doc": pgto["evento__banco_consignacao__pessoajuridica__cnpj"],
            "tipo_doc": "2",  # tipo de inscrição - CNPJ = '2'
            "nome": pgto["evento__banco_consignacao__pessoajuridica__razao_social"],
            "cod_banco": pgto["evento__banco_consignacao__numero"],
            "agencia_num": pgto["evento__banco_consignacao__agencia"],
            "agencia_dv": agencia_dv if agencia_dv else "0",
            "conta_num": pgto["evento__banco_consignacao__conta"],
            "conta_dv": conta_dv if conta_dv else "0",
            "valor_pgto": pgto["total"] * -1,
        }
        if params.get("agencia_num") and params.get("conta_num"):
            if params["cod_banco"] == "001":
                favorecidos_bb.append(consolidar_infos_beneficiario_cnab(**params))
            else:
                favorecidos_outros.append(consolidar_infos_beneficiario_cnab(**params))

    arquivo_cnab = BBCnab240GerarPgto(
        tipo_servico="pgtos_diversos"
    ).criar_cnab_pgto_bb_outros_bancos(
        favorecidos_bb=favorecidos_bb,
        favorecidos_outros=favorecidos_outros,
        data_pgto=data_pgto,
    )

    return arquivo_cnab
