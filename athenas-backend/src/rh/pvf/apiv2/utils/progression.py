from rh.gfp.models import MovimentacaoProgressao


def get_employee_schooling(employee):
    """
    Retorna a estrutra salarial da progressão.
    returns:
    int:
    """
    progressao = get_progression(employee)
    if progressao:
        return progressao.referencia_nivel2d.estrutura_salarial.pk
    else:
        return None


def get_possible_levels(employee):
    """
    Retorna a lista de niveis da progressão
    returns:
    list:
    """
    progressao = get_progression(employee)
    if progressao:
        nivel_atual = progressao.referencia_nivel2d.horizontal
        if nivel_atual == "A":
            niveis = ["B", "C", "D"]
        elif nivel_atual == "B":
            niveis = ["C", "D"]
        elif nivel_atual == "C":
            niveis = ["D"]
        else:
            niveis = []
        return niveis
    else:
        return []


def get_progression(employee):
    """
    Retorna a progressão
    returns:
    object:
    """
    return MovimentacaoProgressao.objects.filter(servidor=employee, ativo=True).first()
