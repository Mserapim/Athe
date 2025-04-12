from contrib.middleware import set_current_user
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema

from apiv2.baseviews import ListBaseView, ApiDetailView
from common.services.apiv2.serializers.historico_servicos import (
    HistoricoServicosSerializer,
)

from common.services.models import HistoricoServico

from contrib.utils import getLogger

log = getLogger(__name__)


class HistoricoServicosView(ListBaseView):
    """
    View da lista de Historico de Servicos
    """

    permission_classes = [IsAuthenticated]
    queryset = HistoricoServico.objects.filter()
    model = HistoricoServico
    serializer_class = HistoricoServicosSerializer
    full_text_index = (
        "servico__name__unaccent__icontains",
        "servico__command__unaccent__icontains",
        "servico__description__unaccent__icontains",
        "ssid__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="servico_id", description="Id do serviço", type=int),
            OpenApiParameter(
                name="executado[]",
                description="Lista de executado: True/False",
                type=bool,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """Retorna os históricos de serviços"""
        return self.list(request, *args, **kwargs)

    def filter_extra_queryset(self, queryset):
        keyword = self.request.query_params.get("keyword", None)
        servico_id = self.request.query_params.get("servico_id", None)
        executado_lista = self.request.query_params.getlist("executado[]", None)

        queryset = HistoricoServico.objects.all()

        if keyword:
            queryset = queryset.filter(
                Q(servico__name__unaccent__icontains=keyword)
                | Q(servico__command__unaccent__icontains=keyword)
                | Q(servico__description__unaccent__icontains=keyword)
                | Q(ssid__icontains=keyword)
            )
        if servico_id:
            queryset = queryset.filter(servico=servico_id)
        if executado_lista:
            queryset = queryset.filter(sucesso__in=executado_lista)

        return queryset.order_by("-iniciado_em")


class HistoricoServicoDetailView(ApiDetailView):
    """
    View de detalhes do histórico do serviço
    """

    model = HistoricoServico
    serializer_class = HistoricoServicosSerializer
