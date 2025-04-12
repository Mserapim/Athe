from standard.models import Choice


def get_objeto_acao(acao, acao_key, desabilitado=False):
    """
    Retorna o dict da ação
    Params:
    - acao
    - acao_key
    - desabilitado
    Retorno:
        (dict) - objeto da ação
    """
    config_acao = Choice.objects.get(name="ACOES_APROVADOR", value=acao)
    return {
        "label": config_acao.label,
        "action": acao_key,
        "disabled": desabilitado,
        "order": config_acao.order_weight,
    }
