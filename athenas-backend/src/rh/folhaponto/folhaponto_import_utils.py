from standard.models import Choice


def normalizar_cpf_origem(cpf_origem):
    """
    Método para tratar o valor do campo cpf da origem da importação.
    Deve retornar uma string com 11 caracteres, completando com '0' (zero) à esquerda
    """

    if len(cpf_origem) == 1:
        return cpf_origem

    qtd = len(cpf_origem)
    if qtd > 11:
        cpf = cpf_origem[(qtd - 11) :]
    else:
        cpf = cpf_origem.rjust(11, "0")

    return cpf


def buscar_tipo_justif(txt_justificativa_origem):
    q_choice = Choice.objects.filter(
        app_label="registerpoint", name="FOLHA_PONTO_TIPO_JUSTIFICATIVA"
    ).filter(label=txt_justificativa_origem)

    if q_choice.exists():
        return q_choice.first().value
    else:
        return None


def normalizar_dados_registro_folhaponto_justif(folha_ponto_justif):
    if folha_ponto_justif.data in [None, ""]:
        return False
    else:
        return {
            "marcacao_hora": folha_ponto_justif.data.time(),
            "marcacao_dia": folha_ponto_justif.data.date(),
            "marcacao": folha_ponto_justif.data,
            "tipo": buscar_tipo_justif(folha_ponto_justif.justificativa),
            "codigo_import": folha_ponto_justif.codigo,
        }


def normalizar_dados_registro_folhaponto_batida(folha_ponto_batida):
    return {
        "marcacao_time": folha_ponto_batida.data.time(),
        "marcacao_hora": folha_ponto_batida.data.time().hour,
        "marcacao_minuto": folha_ponto_batida.data.time().minute,
        "marcacao_dia": folha_ponto_batida.data.date(),
        "marcacao": folha_ponto_batida.data,
        "codigo_import": folha_ponto_batida.pk,
    }
