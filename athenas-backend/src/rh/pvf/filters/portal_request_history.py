from django_filters import FilterSet, CharFilter

from contrib.utils import filtrar_data, getLogger
from rh.models import Servidor
from rh.pvf.models import PortalRequestHistory

log = getLogger(__name__)


class BasePortalRequestHistoryFilter:

    def __init__(self, request=None):
        self.request = request

    @staticmethod
    def filtrar_tipos_acoes(request, queryset):
        tipos_acoes = request.query_params.getlist("tipos_acoes[]")
        if tipos_acoes:
            return queryset.filter(action__in=tipos_acoes).distinct()
        return queryset

    def filtrar_dt_acao(self, queryset, name, value):
        antes = self.request.query_params.get("acao_inicio_em")
        depois = self.request.query_params.get("acao_fim_em")
        if antes or depois:
            queryset = queryset.filter(**filtrar_data("date", antes, depois))
        return queryset.distinct()

    @staticmethod
    def filtrar_usuarios(request, queryset):
        usuarios_param = request.query_params.getlist("usuarios[]")
        if usuarios_param:
            usuarios_param = Servidor.objects.filter(id__in=usuarios_param).values_list(
                "user_id", flat=True
            )
            return queryset.filter(user_id__in=list(usuarios_param))
        return queryset


class PortalRequestHistoryFilters(FilterSet, BasePortalRequestHistoryFilter):
    acao_inicio_em = CharFilter(field_name="date", method="filtrar_dt_acao")
    acao_fim_em = CharFilter(field_name="date", method="filtrar_dt_acao")

    class Meta:
        model = PortalRequestHistory
        fields = ["acao_inicio_em", "acao_fim_em"]
