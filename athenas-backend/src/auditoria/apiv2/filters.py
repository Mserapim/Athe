from rest_framework.filters import BaseFilterBackend


class AuditoriaLogFilters(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filtros = {}
        self.filtrar_acoes(request, filtros)
        self.filtrar_modelos(request, filtros)
        self.filtrar_periodo(request, filtros)
        self.filtrar_keyword(request, filtros)
        return queryset.filter(**filtros)

    def filtrar_acoes(self, request, filtros):
        acoes = request.query_params.getlist("acoes[]")
        if acoes:
            filtros["action__in"] = acoes

    def filtrar_modelos(self, request, filtros):
        modelos_ids = request.query_params.getlist("modelos[]")
        if modelos_ids:
            filtros["content_type__id__in"] = modelos_ids

    def filtrar_periodo(self, request, filtros):
        log_inicio = request.query_params.get("log_inicio_em")
        log_fim = request.query_params.get("log_fim_em")
        if log_inicio and log_fim:
            filtros["timestamp__date__range"] = [log_inicio, log_fim]
        elif log_inicio or log_fim:
            filtros["timestamp__date"] = log_inicio or log_fim

    def filtrar_keyword(self, request, filtros):
        keyword = request.query_params.get("keyword", None)
        if keyword:
            if keyword.isdigit():
                filtros["object_id"] = keyword
            else:
                filtros["actor__username__iexact"] = keyword
