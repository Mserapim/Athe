import requests
from rh.apiv2.serializers.localidade import (
    LocationsSerializer,
    LotacionogramLocationSerializer,
    StateSerializer,
    PaisSerializer,
)
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from auth.backend import MultiAuthentication, CustomTokenJWTAuthentication
from rest_framework.generics import ListAPIView
from apiv2.pagination import CustomPagination
from rh.models import Localidade, Estado, Pais
from rest_framework.response import Response
from apiv2.baseviews import ListBaseView


from contrib.utils import getLogger

log = getLogger(__name__)


class LotacionogramLocationView(ListBaseView):
    """
    VIEW DAS LOCALIDADES PARA O LOTACIONOGRAMA

    Esta classe é responsável por fornecer uma lista paginada de Localidades.

    :queryset: conjunto de objetos do modelo Localidade
    :permission_classes: lista de classes de permissão requeridas para acessar a view
    :authentication_classes: lista de classes de autenticação requeridas para acessar a view
    :pagination_class: classe de paginação personalizada para a view
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Localidade.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination
    serializer_class = LotacionogramLocationSerializer
    full_text_index = ("nome__unaccent__icontains",)

    def get_queryset(self):
        state = self.request.GET.get("estado")
        comarca_id = self.request.GET.get("comarca_id")
        queryset = self.queryset
        if state:
            queryset = queryset.filter(estado=state)
        if comarca_id:
            queryset = queryset.filter(comarca__pk=comarca_id)
        return queryset.order_by("nome")

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        VIEW DAS LOCALIDADES PARA O LOTACIONOGRAMA
        """
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada de Localidades.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LocationsView(ListBaseView):
    """
    View de Localidades

    Esta classe é responsável por fornecer uma lista paginada de Localidades.

    :queryset: conjunto de objetos do modelo Localidade
    :permission_classes: lista de classes de permissão requeridas para acessar a view
    :pagination_class: classe de paginação personalizada para a view
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Localidade.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiAuthentication]
    pagination_class = CustomPagination
    serializer_class = LocationsSerializer
    full_text_index = ("nome__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="estado", description="Estado", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View das localidades
        """
        return self.list(request, *args, **kwargs)

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        estado = self.request.GET.get("estado")

        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset


class StateView(ListBaseView):
    """
    View de Estados

    Esta classe é responsável por fornecer uma lista paginada dos estados.

    :queryset: conjunto de objetos do modelo Localidade
    :permission_classes: lista de classes de permissão requeridas para acessar a view
    :authentication_classes: lista de classes de autenticação requeridas para acessar a view
    :pagination_class: classe de paginação personalizada para a view
    :serializer_class: classe do serializer usado para serializar os objetos da queryset
    """

    queryset = Estado.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiAuthentication]
    pagination_class = CustomPagination
    serializer_class = StateSerializer
    full_text_index = ("nome__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="pais", description="País", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        pais = self.request.GET.get("pais")

        if pais:
            queryset = queryset.filter(pais=pais)
        return queryset


class PaisView(ListBaseView):

    queryset = Pais.objects.all()
    authentication_classes = [MultiAuthentication]
    serializer_class = PaisSerializer
    full_text_index = ("nome__unaccent__icontains",)
