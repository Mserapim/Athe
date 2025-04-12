from apiv2.baseviews import ListBaseView
from contrib.utils import getLogger
from diarias.models import Beneficiario
from diarias.utils.limite_diarias import buscar_limite_uso
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema


log = getLogger()


class LimiteUsoDiariasView(ListBaseView):
    """
    View do Limite e Uso de Diárias
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="meses[]", description="Lista de meses (1-12)", type=str
            ),
            OpenApiParameter(name="ano", description="Ano", type=int),
            OpenApiParameter(
                name="beneficiario_id",
                description="ID do beneficiário cujo servidor terá os limites de uso buscados.",
                type=int,
            ),
        ]
    )
    def list(self, request):
        meses = request.query_params.getlist("meses[]")
        ano = request.query_params.get("ano")
        beneficiario_id = request.query_params.get("beneficiario_id")
        beneficiario = Beneficiario.objects.get(id=beneficiario_id)
        servidor = beneficiario.servidor

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": buscar_limite_uso(servidor, ano, meses),
        }

        return Response(res)
