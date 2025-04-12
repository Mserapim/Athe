from standard.models import Choice


def cancelar_justificativas_request(request):
    """
    Cancela uma solicitação e remove todas as justificativas associadas a ela, se aplicável.

    Args:
        request: Instância da solicitação a ser cancelada.
        status: Status de cancelamento a ser aplicado.
        observation: Observação opcional para o cancelamento.
    """
    from rh.pvf.models import PointJustification

    tipo_folha_ponto = Choice.objects.get(
        app_label="pvf", name="REQUEST_TYPE", label="Folha Ponto"
    )
    if request.request_type == tipo_folha_ponto.value:
        justificativas = PointJustification.objects.filter(
            request=request, cancelado=False
        )
        for justificativa in justificativas:
            justificativa.delete()
