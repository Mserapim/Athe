from django.conf import settings
from auth.backend import MultiAuthentication
from contrib.middleware import set_current_user
from apiv2.baseviews import ApiDetailView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from contrib.utils import getLogger
from rh.apiv2.serializers.teletrabalho import MovimentacaoTeletrabalhoSerializer
from rh.models import MovimentacaoTeletrabalho


log = getLogger(__name__)


class MovimentacaoTeletrabalhoDetailView(ApiDetailView):
    """
    View da movimentação de teletrabalho
    """

    model = MovimentacaoTeletrabalho
    serializer_class = MovimentacaoTeletrabalhoSerializer
    authentication_classes = [MultiAuthentication]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id", description="Chave primario(Primary Key)", type=int
            ),
            OpenApiParameter(
                name="servidor_id", description="id do servidor (Primary Key)", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Descrição da operação GET
        Retorna o objeto referente ao id informado pelos query_params
        Parâmetros:
        - id: Chave primaria do objeto.
        """
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        id = request.query_params.get("id", None)
        servidor_id = request.query_params.get("servidor_id", None)
        if servidor_id:
            mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
                servidor__pk=servidor_id
            ).last()
            id = mov_teletrabalho.pk if mov_teletrabalho else id
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, id=id)
        serializer = self.serializer_class(item)
        return Response(serializer.data)
