from apiv2.baseviews import ListBaseView
from rest_framework.response import Response

from diarias.apiv2.serializers.choices import ChoicesDiariasSerializer
from standard.models import Choice

from contrib.utils import getLogger

log = getLogger(__name__)


class SituacoesDiariasApiList(ListBaseView):

    serializer_class = ChoicesDiariasSerializer
    model = Choice

    def get_queryset(self):
        return Choice.objects.filter(
            app_label="diarias", name="SITUACAO_SOLICITACAO_VIAGEM"
        )


class MotivosViagemDiariasApiList(ListBaseView):

    serializer_class = ChoicesDiariasSerializer
    model = Choice

    def get_queryset(self):
        return Choice.objects.filter(app_label="diarias", name="MOTIVO_VIAGEM")


class FinalidadesDiariasApiList(ListBaseView):

    serializer_class = ChoicesDiariasSerializer
    model = Choice
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        return Choice.objects.filter(
            app_label="diarias", name="FINALIDADE_VIAGEM"
        ).order_by("label")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.order_queryset(queryset)

        exportar = request.GET.get("exportar", None)
        if exportar:
            sincrono = request.GET.get("sincrono", False)
            campos = request.GET.getlist("colunas[]", [])
            return self.exportar_arquivo(exportar, campos, sincrono, queryset)

        serializer = self.get_serializer(queryset, many=True)

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": serializer.data,
        }

        return Response(res)


class EtapasDiariasApiList(ListBaseView):

    serializer_class = ChoicesDiariasSerializer
    model = Choice

    def get_queryset(self):
        return Choice.objects.filter(
            app_label="diarias", name="ETAPA_SOLICITACAO_VIAGEM"
        )


class AcompAutoridadeDiariasApiList(ListBaseView):

    serializer_class = ChoicesDiariasSerializer
    model = Choice

    def get_queryset(self):
        return Choice.objects.filter(
            app_label="diarias", name="ACOMPANHAMENTO_AUTORIDADE"
        )


class TipoSolicitanteDiariasApiList(ListBaseView):

    serializer_class = ChoicesDiariasSerializer
    model = Choice

    def get_queryset(self):
        return Choice.objects.filter(app_label="diarias", name="TIPO_SOLICITANTE")
