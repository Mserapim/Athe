from django.db.models import Prefetch, CharField
from django.db.models.functions import Cast

from apiv2.baseviews import ListBaseView
from rh.pvf.models import PortalRequest, PortalRequestHistory
from rh.pvf.filters.portal_request import PortalRequestFilters
from rh.pvf.filters.portal_request_history import BasePortalRequestHistoryFilter
from rh.apiv2.serializers.gestao_pvf import PortalRequestSerializer


class GestaoPVFView(ListBaseView):
    serializer_class = PortalRequestSerializer
    filterset_class = PortalRequestFilters
    full_text_index = (
        "identificacao__icontains",
        "matricula__icontains",
        "employee__pessoa_fisica__nome__unaccent__icontains",
    )

    def get_queryset(self):
        queryset = PortalRequest.objects.prefetch_related(
            Prefetch(
                "portalrequesthistory_set",
                queryset=self.prefetch_queryset(),
            )
        ).annotate(
            matricula=Cast("employee__matricula", output_field=CharField()),
            identificacao=Cast("id", output_field=CharField()),
        )
        return queryset

    def filter_extra_queryset(self, queryset):
        filtros = self.filterset_class()
        queryset = filtros.filtrar_historico(self.request, queryset)
        queryset = filtros.filtrar_tipos_solicitacoes(self.request, queryset)
        queryset = filtros.filtrar_situacoes(self.request, queryset)
        queryset = filtros.filtrar_categorias(self.request, queryset)
        filtrar_por = self.request.query_params.get("filtrar_por", "")
        if filtrar_por == "solicitacao":
            queryset = filtros.filtrar_usuarios(self.request, queryset)
        return queryset

    def prefetch_queryset(self):
        filtros = BasePortalRequestHistoryFilter(request=self.request)
        queryset = PortalRequestHistory.objects.order_by("-date")
        queryset = filtros.filtrar_tipos_acoes(self.request, queryset)
        queryset = filtros.filtrar_dt_acao(queryset, None, None)
        filtrar_por = self.request.query_params.get("filtrar_por", "")
        if filtrar_por == "acao":
            queryset = filtros.filtrar_usuarios(self.request, queryset)
        return queryset
