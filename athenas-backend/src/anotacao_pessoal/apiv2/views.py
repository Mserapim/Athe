from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status


from contrib.middleware import set_current_user
from django.shortcuts import get_object_or_404


from anotacao_pessoal.apiv2.serializers import (
    AnotacaoPessoalSerializer,
    TiposAnotacaoSerializer,
    TiposDocumentoSerializer,
    AnotacaoPessoalCompletoSerializer,
)
from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from contrib.utils import getLogger

from anotacao_pessoal.models import AnotacaoPessoal
from rh.models import Servidor
from standard.models import Choice
from itertools import chain

log = getLogger(__name__)


class AnotacaoPessoalView(ListBaseView):
    """
    View da lista anotações pessoais
    """

    permission_classes = [IsAuthenticated]
    queryset = AnotacaoPessoal.objects.filter()
    serializer_class = AnotacaoPessoalSerializer

    def get_queryset(self):
        servidor = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(servidor__pk=servidor.pk)

        params = self.request.query_params
        tipo_anotacao_ids = params.get("tipo_anotacao_id", None)
        if tipo_anotacao_ids:
            tipo_anotacao_id_list = tipo_anotacao_ids.split(",")
            queryset = queryset.filter(tipo__in=tipo_anotacao_id_list)

        return self.filter_queryset(queryset)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do lista anaotações pessoais
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TiposAnotacaoView(ListBaseView):
    """
    View para retornar os Tipos de Anotação - de Anotação Pessoal
    """

    permission_classes = [IsAuthenticated]
    queryset = (
        Choice.objects.values("value", "label")
        .filter(app_label="rh", name="TIPO_ANOTACAO")
        .order_by("label")
    )
    serializer_class = TiposAnotacaoSerializer

    full_text_index = ("label__icontains",)

    def include_id_informado(self, page):
        params = self.request.query_params
        id = params.get("id")
        if id:
            queryset_id = self.get_queryset().filter(value=id)
            page = list(chain(queryset_id, page))

        return page


class TiposDocumentosView(ListBaseView):
    """
    View para retornar os Tipos de Anotação - de Anotação Pessoal
    """

    permission_classes = [IsAuthenticated]
    queryset = (
        Choice.objects.values("value", "label")
        .filter(app_label="rh", name="TIPO_DOCUMENTO")
        .order_by("label")
    )
    serializer_class = TiposDocumentoSerializer
    full_text_index = ("label__icontains",)

    def include_id_informado(self, page):
        params = self.request.query_params
        id = params.get("id")
        if id:
            queryset_id = self.get_queryset().filter(value=id)
            page = list(chain(queryset_id, page))

        return page


class AnotacaoPessoalListView(ListBaseView):
    """
    View de Anotacão Pessoal
    """

    model = AnotacaoPessoal
    serializer_class = AnotacaoPessoalCompletoSerializer

    full_text_index = (
        "servidor__matricula__iexact",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__social_name__icontains",
        "servidor__pessoa_fisica__cpf__iexact",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="tipos_anotacao[]", description="Tipos de Anotação", type=int
            ),
            OpenApiParameter(
                name="tipos_documento[]", description="Tipos de Documento", type=int
            ),
            OpenApiParameter(name="servidor_id", description="Servidor", type=int),
            OpenApiParameter(name="servidor_ids[]", description="Servidor", type=int),
            OpenApiParameter(name="ocultos[]", description="Ocultos", type=bool),
        ]
    )
    def get_queryset(self):
        return self.model.objects.get_queryset_all()

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        params = self.request.query_params
        tipo_anotacao_ids = params.getlist("tipos_anotacao[]", None)
        if tipo_anotacao_ids:
            queryset = queryset.filter(tipo__in=tipo_anotacao_ids)

        tipo_documento_ids = params.getlist("tipos_documento[]", None)
        if tipo_documento_ids:
            queryset = queryset.filter(documento_tipo__in=tipo_documento_ids)

        servidor_id = params.get("servidor_id", None)
        if servidor_id:
            queryset = queryset.filter(servidor=servidor_id)

        servidor_ids = params.getlist("servidor_ids[]", [])
        if servidor_ids:
            queryset = queryset.filter(servidor__in=servidor_ids)

        ocultos = params.getlist("ocultos[]", [])
        if ocultos and "" not in ocultos:
            queryset = queryset.filter(exibir__in=ocultos)

        return queryset


class AnotacaoPessoalViewSet(ApiCore):
    """
    View de Anotacão Pessoal
    """

    model = AnotacaoPessoal
    serializer_class = AnotacaoPessoalCompletoSerializer

    path_function_map = {"criar": "create", "editar": "update", "ocultar": "ocultar"}

    def ocultar(self, request, *args, **kwargs):
        set_current_user(request.user)
        instance = self.get_object()
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        instance.exibir = False
        instance.save()
        rst.update({"success": True, "message": "Registro ocultado com sucesso"})

        return Response(rst, status=rst["code"])


class AnotacaoPessoalDetailView(ApiDetailView):
    model = AnotacaoPessoal
    serializer_class = AnotacaoPessoalCompletoSerializer
