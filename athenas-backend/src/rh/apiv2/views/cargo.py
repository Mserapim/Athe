from apiv2.utils import response_api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema
from apiv2.baseviews import ApiCore, ApiDetailView, BaseViewSet, ListBaseView
from rh.apiv2.filters.cargo import CargoFilters
from rh.apiv2.utils import get_cargo_posse_stats
from rh.const import INDICATIVO, TIPO_LEI_CARGO, TIPO_NIVEL_ESCOLARIDADE
from rh.models import Cargo
from auth.backend import CustomTokenJWTAuthentication
from rh.apiv2.serializers.cargo import (
    AreaTrabalhoCargoSerializer,
    CargoSerializer,
    JobPositionSerializer,
)


class JobPositionViewSet(BaseViewSet):
    """
    View dos cargos
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    queryset = Cargo.objects.filter(ativo=True)
    serializer_class = JobPositionSerializer
    full_text_index = ("nome__icontains",)

    def get_queryset(self):
        queryset = self.queryset.filter(
            quadro__movimentacaoposse__isnull=False,
            quadro__movimentacaoposse__ativo=True,
        ).distinct()
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CargoView(ListBaseView):
    model = Cargo
    serializer_class = CargoSerializer
    full_text_index = ("nome__unaccent__icontains",)
    filterset_class = CargoFilters

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="ativo", description="Ativo", type=bool),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Cargo.objects.all()
        filtros = self.filterset_class()
        queryset = filtros.filter_tipo_lei_cargos(self.request, queryset)
        queryset = filtros.filter_niveis_escolaridade(self.request, queryset)
        queryset = filtros.filter_ativo(self.request, queryset)
        return queryset


class AreaTrabalhoCargoView(ListBaseView):
    model = Cargo
    serializer_class = AreaTrabalhoCargoSerializer
    full_text_index = ("nome__unaccent__icontains",)
    filterset_class = CargoFilters

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="ativo", description="Ativo", type=bool),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Cargo.objects.all()
        filtros = self.filterset_class()
        queryset = filtros.filter_tipo_lei_cargos(self.request, queryset)
        queryset = filtros.filter_niveis_escolaridade(self.request, queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.order_queryset(queryset)

        exportar = request.GET.get("exportar", None)
        if exportar:
            sincrono = request.GET.get("sincrono", False)
            campos = request.GET.getlist("colunas[]", [])
            return self.exportar_arquivo(exportar, campos, sincrono, queryset)

        cargo_stats = get_cargo_posse_stats(queryset)
        page = self.paginate_queryset(queryset)
        page = self.include_id_informado(page)

        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"cargo_stats": cargo_stats}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset, many=True, context={"cargo_stats": cargo_stats}
        )
        return response_api_view(serializer.data)


class CargoCoreView(ApiCore):
    """
    CRUD do cadastro de cargos
    """

    model = Cargo
    serializer_class = CargoSerializer


class CargoDetailView(ApiDetailView):
    """
    View do detalhe de cargos
    """

    model = Cargo
    serializer_class = CargoSerializer


class TipoLeiCargoView(ListBaseView):
    """
    View da config do tipo lei cargo
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="palavra_chave", description="Campo de Pesquisa", type=str
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Config do tipo lei cargo
        """
        palavra_chave = request.GET.get("palavra_chave", "").strip().lower()

        lista_dict = [
            {"valor": valor, "display": display}
            for valor, display in TIPO_LEI_CARGO
            if palavra_chave in display.lower()
        ]

        return response_api_view(lista_dict)


class IndicativoCargoView(ListBaseView):
    """
    View da config do indicativo do cargo
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="palavra_chave", description="Campo de Pesquisa", type=str
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Config do indicativo do cargo
        """
        palavra_chave = request.GET.get("palavra_chave", "").strip().lower()

        lista_dict = [
            {"valor": valor, "display": display}
            for valor, display in INDICATIVO
            if palavra_chave in display.lower()
        ]

        return response_api_view(lista_dict)


class TipoNivelEscolaridadeView(ListBaseView):
    """
    View para listar os tipos de nível de escolaridade
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="palavra_chave", description="Campo de Pesquisa", type=str
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista os tipos de nível de escolaridade com opção de filtragem por palavra-chave
        """
        palavra_chave = request.GET.get("palavra_chave", "").strip().lower()

        lista_dict = [
            {"valor": valor, "display": display}
            for valor, display in TIPO_NIVEL_ESCOLARIDADE
            if palavra_chave in display.lower()
        ]

        return response_api_view(lista_dict)
