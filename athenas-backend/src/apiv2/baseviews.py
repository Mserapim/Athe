from apiv2.response import ResponseExportar
from contrib.base_converter import str_to_bool
import pyexpat
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import (
    ListAPIView,
    GenericAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    RetrieveAPIView,
)
from django_filters import rest_framework as filters
from django.db.models import Q
from apiv2.pagination import CustomPagination
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from django.http import Http404
from itertools import chain

from rest_framework.views import APIView

from contrib.middleware import set_current_user
from django.shortcuts import get_object_or_404


from contrib.utils import getLogger

log = getLogger(__name__)


class BaseViewSet(GenericViewSet):
    """
    View base

    :permission_classes: lista de classes de permissão requeridas para acessar a view
    :pagination_class: classe de paginação personalizada para a view
    :filter_backends: tupla de filtros padrão
    :full_text_index: tupla de campos filtrados
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    full_text_index = ()

    def filter_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend e o valor da pesquisa keyword
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)

        keyword = self.request.GET.get("keyword")
        if not keyword:
            keyword = self.request.GET.get("palavra_chave")
        if self.full_text_index and keyword:
            qf = None

            for index in self.full_text_index:
                q = Q(**{index: keyword})
                qf = q if qf is None else Q(qf | q)

            queryset = queryset.filter(qf)

        return queryset


class ListBaseView(ListAPIView):
    """
    View base para api's de listagem

    :permission_classes: lista de classes de permissão requeridas para acessar a view
    :pagination_class: classe de paginação personalizada para a view
    :filter_backends: tupla de filtros padrão
    :full_text_index: tupla de campos filtrados
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    full_text_index = ()

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="exportar",
                description="Formato do arquivo a ser exportado",
                type=str,
            ),
            OpenApiParameter(
                name="sincrono",
                description="informar a execução do download",
                type=bool,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada.
        """
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.order_queryset(queryset)

        exportar = request.GET.get("exportar", None)

        if exportar:
            sincrono = request.GET.get("sincrono", False)
            campos = request.GET.getlist("colunas[]", [])
            return self.exportar_arquivo(exportar, campos, sincrono, queryset)

        page = self.paginate_queryset(queryset)

        page = self.include_id_informado(page)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def include_id_informado(self, page):
        params = self.request.query_params
        id = params.get("id")
        if id:
            queryset_id = self.get_queryset().filter(id=id)
            if queryset_id.exists():
                item_selecionado = queryset_id.first()
                if item_selecionado in page:
                    page.remove(item_selecionado)

            queryset_id = self.get_queryset().filter(id=id)
            page = list(chain(queryset_id, page))

        return page

    def filter_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend e o valor da pesquisa keyword e palavra_chave
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)

        keyword = self.request.GET.get("keyword")
        if keyword is None:
            keyword = self.request.GET.get("palavra_chave")

        if self.full_text_index and keyword:
            qf = None

            for index in self.full_text_index:
                q = Q(**{index: keyword})
                qf = q if qf is None else Q(qf | q)

            queryset = queryset.filter(qf)

        queryset = self.filter_extra_queryset(queryset)

        return queryset

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        return queryset

    def order_queryset(self, queryset):
        """
        Realiza a ordenaação dos valores do queryset, recebendo valores, do front,
        """

        order_by = self.request.query_params.get("order_by", None)
        model = self.serializer_class.Meta.model

        if hasattr(self.serializer_class, "ORDER_BY_MAP"):
            order_by_map = self.serializer_class.ORDER_BY_MAP
            map_keys = list(order_by_map.keys())
        else:
            order_by_map = []
            map_keys = []

        fields_model = [field.name for field in model._meta.get_fields()]

        if order_by:
            order_by = order_by.replace(" ", "")
            order_by = order_by.split(",")

            for indice, campo in enumerate(order_by):
                if (
                    campo.replace("-", "") not in fields_model
                    and campo.replace("-", "") not in map_keys
                ):
                    order_by.remove(campo)

                if campo.replace("-", "") in map_keys:
                    campo = campo.replace("-", "")
                    order_by[indice] = order_by[indice].replace(
                        campo, order_by_map[campo]
                    )

            queryset = queryset.order_by(*order_by)
        else:
            queryset = queryset.order_by("id")
        return queryset

    def exportar_arquivo(self, exportar, colunas, sincrono, dados):
        """
        Exporta arquivo CSV, seja a partir de queryset com serializer ou lista de dicionários.
        """
        set_current_user(self.request.user)
        sincrono = str_to_bool(sincrono) if sincrono else sincrono

        if isinstance(dados, list):
            data_queryset = {
                "dados_lista": dados,
                "serializer_name": None,
            }
            dados_lista = True
        else:
            serializer_class = self.get_serializer_class()
            data_queryset = {
                "queryset": dados,
                "serializer_name": f"{serializer_class.__module__}.{serializer_class.__name__}",
            }
            dados_lista = False

        response_exportar = ResponseExportar(
            data_queryset,
            formato=exportar,
            sincrono=sincrono,
            campos=colunas,
            dados_lista=dados_lista,
        )

        return response_exportar.response if sincrono else response_exportar


class ApiDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    full_text_index = ()
    model = None  # Defina o modelo como None inicialmente

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id", description="Chave primario(Primary Key)", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Descrição da operação GET

        Retorna o objeto referente ao id informado pelos query_params

        Parâmetros:
        - id: Chave primaria do objeto.
        """

        return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()

    def retrieve(self, request, *args, **kwargs):
        id = self.request.query_params.get("id", None)
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, id=id)
        serializer = self.serializer_class(item)
        return Response(serializer.data)


class ApiCore(CreateAPIView, UpdateAPIView, DestroyAPIView):

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend,)
    http_method_names = ["post"]
    full_text_index = ()
    model = None  # Defina o modelo como None inicialmente

    # Mapeamento de caminho para função
    path_function_map = {"criar": "create", "editar": "update", "apagar": "exclude"}

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id", description="Chave primario(Primary Key)", type=int
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        """
        Descrição da operação GET

        execulta uma função diacordo com o path da requisição

        Parâmetros:
        - id: Chave primaria do objeto.
        """

        path = request.path

        for keyword, func_name in self.path_function_map.items():
            if keyword in path:
                if func_name == "update":
                    kwargs["partial"] = True
                func = getattr(self, func_name)
                return func(request, *args, **kwargs)

        return Response(
            {"message": "Método não suportado"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def get_queryset(self):
        return self.model.objects.all()

    def get_object(self):
        """
        Mudando a função get_object para pegar o id pelo data
        """
        id = self.request.data.get("id", None)

        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:

            if id is not None:
                raise Http404("O objeto não existe para o id fornecido")
            raise Http404("O parametro id não foi fornecido")

    def create(self, request, *args, **kwargs):
        set_current_user(request.user)
        serializer = self.get_serializer(data=request.data)
        response = serializer.perform_create()
        return Response(response, status=response["code"])

    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        response = serializer.perform_update(instance)
        return Response(response, status=response["code"])

    def exclude(self, request, *args, **kwargs):
        resposta = {"code": 200, "datail": "Nada Feito"}

        try:
            set_current_user(request.user)
            instance = self.get_object()
            instance.delete()

            resposta["datail"] = "Item Excluido"

        except self.model.DoesNotExist:
            resposta["datail"] = "O objeto não existe ou já foi excluido"
            resposta["code"] = 400
        except Exception as e:
            resposta["datail"] = f"Erro ao tentar excluir o item - {e}"
            resposta["code"] = 400

        return Response(resposta, status=resposta["code"])
