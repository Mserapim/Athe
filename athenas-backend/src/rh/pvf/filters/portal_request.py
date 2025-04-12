from django_filters import FilterSet, CharFilter

from contrib.utils import filtrar_data, getLogger
from rh.models import Servidor
from rh.pvf.models import PortalRequest

log = getLogger(__name__)


class PortalRequestFilters(FilterSet):
    solicitacao_inicio_em = CharFilter(
        field_name="date", method="filtrar_dt_solicitacao"
    )
    solicitacao_fim_em = CharFilter(field_name="date", method="filtrar_dt_solicitacao")

    class Meta:
        model = PortalRequest
        fields = [
            "solicitacao_inicio_em",
            "solicitacao_fim_em",
        ]

    def filtrar_historico(self, request, queryset):
        usuarios_param = request.query_params.getlist("usuarios[]")
        antes = request.query_params.get("acao_inicio_em")
        depois = request.query_params.get("acao_fim_em")
        tipos_acoes = request.query_params.getlist("tipos_acoes[]")
        filtrar_por = request.query_params.get("filtrar_por", "")

        filtros = {}
        if usuarios_param and filtrar_por == "acao":
            usuarios_param = Servidor.objects.filter(id__in=usuarios_param).values_list(
                "user_id", flat=True
            )
            filtros["portalrequesthistory__user_id__in"] = list(usuarios_param)
        if antes and depois:
            filtros["portalrequesthistory__date__range"] = [antes, depois]
        if tipos_acoes:
            filtros["portalrequesthistory__action__in"] = tipos_acoes
        return queryset.filter(**filtros).distinct()

    @staticmethod
    def filtrar_usuarios(request, queryset):
        usuarios_param = request.query_params.getlist("usuarios[]")
        if usuarios_param:
            return queryset.filter(employee__id__in=usuarios_param).distinct()
        return queryset

    @staticmethod
    def filtrar_tipos_solicitacoes(request, queryset):
        solicitacoes = request.query_params.getlist("tipos_solicitacoes[]")
        if solicitacoes:
            return queryset.filter(portal_request_type__in=solicitacoes).distinct()
        return queryset

    @staticmethod
    def filtrar_situacoes(request, queryset):
        situacoes = request.query_params.getlist("situacoes[]")
        if situacoes:
            return queryset.filter(status__in=situacoes).distinct()
        return queryset

    def filtrar_dt_solicitacao(self, queryset, name, value):
        antes = self.request.query_params.get("solicitacao_inicio_em")
        depois = self.request.query_params.get("solicitacao_fim_em")
        if antes or depois:
            queryset = queryset.filter(**filtrar_data(name, antes, depois))
        return queryset.distinct()

    @staticmethod
    def filtrar_categorias(request, queryset):
        categorias_param = request.query_params.getlist("categorias[]")
        if categorias_param:
            type_by_possessions = []
            for employee_type in categorias_param:
                if employee_type == "SERVIDOR":
                    type_by_possessions.extend(
                        ["EFE", "CMS", "ECM", "RCM", "RFC", "EFC", "REQ", "VOL", "EXT"]
                    )
                elif employee_type == "MEMBRO":
                    type_by_possessions.extend(["MBR", "MEL", "MEC"])
                elif employee_type == "ESTAGIARIO":
                    type_by_possessions.extend(["EST"])
                elif employee_type == "RESIDENTE":
                    type_by_possessions.extend(["RES"])
            return queryset.filter(
                employee__type_by_possession__in=type_by_possessions
            ).distinct()
        return queryset
