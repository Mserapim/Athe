from django_filters import rest_framework as filters
from rh.models import Cargo
import django_filters
from drf_spectacular.utils import extend_schema_field


class CargoFilters(django_filters.FilterSet):
    """
    Filtros da api de cargos
    """

    tipo_lei_cargos = filters.CharFilter(method="filter_tipo_lei_cargos")
    niveis_escolaridade = filters.NumberFilter(method="filter_niveis_escolaridade")
    ativo = filters.NumberFilter(method="filter_ativo")

    class Meta:
        model = Cargo
        fields = ["ativo", "tipo_lei_cargos", "niveis_escolaridade"]

    @extend_schema_field(
        {
            "description": "tipo_lei_cargos[]",
            "type": "array",
            "items": {"type": "string"},
        }
    )
    def filter_tipo_lei_cargos(self, request, queryset):
        tipos = request.GET.getlist("tipo_lei_cargos[]")
        if tipos:
            return queryset.filter(tipo_lei_cargo__in=tipos)

        return queryset

    @extend_schema_field(
        {
            "description": "niveis_escolaridade[]",
            "type": "array",
            "items": {"type": "integer"},
        }
    )
    def filter_niveis_escolaridade(self, request, queryset):
        niveis = request.GET.getlist("niveis_escolaridade[]")
        if niveis:
            return queryset.filter(configs__educational_level__in=niveis)

        return queryset.distinct()

    @extend_schema_field(
        {
            "description": "ativo[]",
            "type": "array",
            "items": {"type": "boolean"},
        }
    )
    def filter_ativo(self, request, queryset):
        ativos = request.GET.getlist("ativo[]")
        if ativos:
            ativos = [val.lower() == "true" for val in ativos]
            return queryset.filter(ativo__in=ativos)
        return queryset
