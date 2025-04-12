from auditoria.apiv2.filters import AuditoriaLogFilters
from auditoria.apiv2.serializers import AuditoriaLogSerializer, ModeloLogSerializer
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from apiv2.baseviews import ListBaseView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes


class AuditoriaLogView(ListBaseView):
    """
    View da auditoria de logs
    """

    model = LogEntry
    serializer_class = AuditoriaLogSerializer
    filter_backends = (AuditoriaLogFilters,)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="acoes[]",
                description="Ações",
                type={"type": "array", "items": {"type": "integer"}},
            ),
            OpenApiParameter(
                name="modelos[]",
                description="id modelos",
                type={"type": "array", "items": {"type": "integer"}},
            ),
            OpenApiParameter(
                name="log_inicio_em",
                description="Inicio dos logs",
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                name="log_fim_em", description="Fim dos logs", type=OpenApiTypes.DATE
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View da auditoria de logs
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def filter_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        queryset = self.filter_extra_queryset(queryset)
        return queryset


class ModelosLogView(ListBaseView):
    """
    Lista os modelos.
    """

    model = ContentType
    serializer_class = ModeloLogSerializer
    full_text_index = ("model__icontains",)

    @extend_schema(
        summary="Lista os modelos",
        description="Retorna os modelos.",
    )
    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
