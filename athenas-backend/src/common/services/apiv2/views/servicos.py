from contrib.middleware import set_current_user

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer

from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView, BaseViewSet
from apiv2.utils import response_api_view
from common.services.apiv2.serializers.servicos import (
    ServicosSerializer,
    MensagensServicoSerializer,
)
from common.services.api.services import SvcScheduledServicesRestful

from common.services.models import ScheduledServices, HistoricoServico
from engine.mq.models import TaskMessages

from contrib.utils import getLogger

log = getLogger(__name__)


class ServicosView(ListBaseView):
    """
    View da lista de Servicos
    """

    permission_classes = [IsAuthenticated]
    queryset = ScheduledServices.objects.filter()
    serializer_class = ServicosSerializer
    full_text_index = (
        "name__icontains",
        "command__icontains",
        "description__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="executado[]",
                description="Lista de executado: True/False",
                type=bool,
            ),
        ]
    )
    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        executado_lista = self.request.query_params.getlist("executado[]", None)

        if executado_lista:
            queryset = queryset.filter(executado__in=executado_lista)

        return queryset


class ServicosDetailView(ApiDetailView):
    """
    View de detalhes de Servico
    """

    model = ScheduledServices
    serializer_class = ServicosSerializer


class ServicosApicoreView(ApiCore):
    """
    View da Criar, editar e apagar de Servico
    """

    model = ScheduledServices
    serializer_class = ServicosSerializer
    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
        "executar-servico": "executar_servico",
    }

    def executar_servico(self, request, *args, **kwargs):
        set_current_user(request.user)

        servico_id = request.data.get("id")
        resposta = SvcScheduledServicesRestful.execute_job(
            ScheduledServices.objects.get(pk=servico_id), params={"api": True}
        )

        return Response(resposta, status=resposta["code"])


class MensagensServicoView(BaseViewSet):
    """
    View da lista de mensagens de um serviço
    """

    permission_classes = [IsAuthenticated]
    queryset = TaskMessages.objects.filter()
    serializer_class = MensagensServicoSerializer

    @action(detail=True, methods=["GET"])
    def mensagens(self, request, pk=None):
        keyword = request.query_params.get("keyword")

        historico_servico = HistoricoServico.objects.get(pk=pk)
        queryset = self.queryset.filter(tasker__uuid=historico_servico.ssid).order_by(
            "tasker__started_task"
        )

        if keyword:
            queryset = queryset.filter(message__unaccent__icontains=keyword)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)

    def get_queryset(self):
        return self.filter_queryset(self.queryset)
