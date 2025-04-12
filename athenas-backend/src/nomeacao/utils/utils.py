from datetime import datetime

from standard.models import Choice

from rh.models import Estado, Localidade, Banco

from nomeacao.const import ORIENTACAO_SEXUAL, TIPO_SANGUE, FATOR_RH


def normalizar_cpf(cpf):
    return cpf.replace(".", "").replace("-", "")


def normalizar_nome_social(pf_convidado):
    return (
        pf_convidado.nome_social
        if pf_convidado.nome_social not in [None, ""]
        else pf_convidado.nome_completo
    )


def normalizar_rg_orgao(rg_orgao):
    return rg_orgao if (rg_orgao is not None and len(rg_orgao)) <= 10 else ""


def buscar_uf(sigla_uf):
    try:
        return Estado.objects.filter(sigla=sigla_uf).first()
    except:
        return None


def buscar_municipio(municipio_id):
    try:
        return Localidade.objects.get(pk=municipio_id)
    except:
        return None


def buscar_tipo_endereco_choice(tipo_endereco):
    try:
        return (
            Choice.objects.filter(
                app_label="rh", name="TYPE_ADDRESS", label=tipo_endereco.title()
            )
            .first()
            .value
        )
    except:
        return None


def buscar_tipo_logr_choice(tipo_endereco):
    try:
        return (
            Choice.objects.filter(
                app_label="rh", name="TYPE_STREET", label=tipo_endereco.upper()
            )
            .first()
            .value
        )
    except:
        return None


def buscar_tipo_tel_choice():
    return (
        Choice.objects.filter(app_label="rh", name="TYPE_PHONE", label="CELULAR")
        .first()
        .value
    )


def normalizar_sangue_doador(sangue_doador):
    return True if sangue_doador in [1, "1"] else False


def normalizar_data_str_date(data, separador):
    ano = data.split(separador)[0]
    mes = data.split(separador)[1]
    dia = data.split(separador)[2]

    try:
        return datetime(ano, mes, dia).date()
    except:
        return None


def buscar_banco(banco):
    try:
        return Banco.objects.filter(numero=banco.split("-")[0].strip()).first()
    except:
        return None


def normalizar_tipo_conta(tipo_conta):
    if "corrente" in tipo_conta:
        return 1  # Choice TIPO_CONTA - CORRENTE
    elif "poup" in tipo_conta:
        return 2  # Choice TIPO_CONTA - POUPANÇA
    elif "sal" in tipo_conta:
        return 3  # Choice TIPO_CONTA - SALÁRIO
    else:
        return None


def buscar_dados_bancarios(pf_athenas, banco, tipo_conta, num_agencia, num_conta):
    return pf_athenas.dadosbancarios.filter(
        banco=banco,
        tipo_conta=tipo_conta,
        agencia=num_agencia,
        conta_corrente_completa=num_conta,
    )


def normalizar_orientacao_sexual(orientacao_sexual):
    try:
        return ORIENTACAO_SEXUAL[orientacao_sexual]
    except:
        return 5  # Não Informado


def normalizar_tipo_sangue(tipo_sangue):
    try:
        return TIPO_SANGUE[tipo_sangue]
    except:
        return 5  # Não Informado


def normalizar_fator_rh(fator_rh):
    try:
        return FATOR_RH[fator_rh]
    except:
        return 3  # Não Informado
