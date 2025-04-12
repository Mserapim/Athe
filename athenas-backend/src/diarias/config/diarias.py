from standard.models import Choice


class FluxoDiarias(object):
    """
    Classe com métodos e lógicas para funcionalidades sobre fluxo de diárias
    """

    def buscar_todas_etapas(self):
        """
        Método que retorna uma lista de todas as etapas disponíveis no sistema
        """
        return (
            Choice.objects.filter(app_label="diarias", name="ETAPA_SOLICITACAO_VIAGEM")
            .order_by("label")
            .values("value", "label")
        )

    def buscar_todas_situacoes(self):
        """
        Método que retorna uma lista de todas as situações disponíveis no sistema
        """
        return (
            Choice.objects.filter(
                app_label="diarias", name="SITUACAO_SOLICITACAO_VIAGEM"
            )
            .order_by("label")
            .values("value", "label")
        )

    def buscar_todas_condicionais(self):
        """
        Método que retorna uma lista de todas as condicionais disponíveis no sistema
        """
        return (
            Choice.objects.filter(
                app_label="diarias", name="CONDICIONAIS_FLUXO_DIARIAS"
            )
            .order_by("label")
            .values("value", "label")
        )
