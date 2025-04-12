from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rh.apiv2.serializers.publicacao import (
    PublicacaoSerializer,
    VeiculoPublicacaoSerializer,
    PublicationSerializer,
)
from rh.models import Publicacao
from standard.models import Choice
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apiv2.baseviews import BaseViewSet
from rh.models import Publicacao
from auth.backend import MultiAuthentication
from rest_framework.pagination import PageNumberPagination
from anotacao_pessoal.models import AnotacaoPessoal

log = getLogger(__name__)


class PublicacaoListView(ListBaseView):
    """
    View de Membros Trabalho Remoto
    """

    model = Publicacao
    serializer_class = PublicacaoSerializer
    queryset = Publicacao.objects.filter()

    full_text_index = (
        "cache_unicode__icontains",
        "interessado_nome__unaccent__icontains",
        "document__unaccent__icontains",
        "numero__exact",
        "numero_publicacao__exact",
        "observacao__unaccent__icontains",
    )

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
            OpenApiParameter(name="status", description="Status", type=int),
            OpenApiParameter(name="tipo", description="tipo publicação", type=int),
            OpenApiParameter(
                name="tipo_anotacao", description="tipo anotacao vinculada", type=int
            ),
            OpenApiParameter(name="id", description="id da publicacao", type=int),
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

        params = self.request.query_params
        status = params.getlist("status[]", None)
        if status:
            queryset = queryset.filter(publication_state__in=status)

        tipo = params.getlist("tipo[]")

        if tipo:
            queryset = queryset.filter(tipo__in=tipo)

        tipo_anotacao = params.get("tipo_anotacao")

        if tipo_anotacao:
            queryset = queryset.filter(
                anotacao_pessoal__isnull=False, anotacao_pessoal__tipo=tipo_anotacao
            )

        return queryset


class PublicacaoDetailView(ApiDetailView):
    """
    Detalhess de Membros Trabalho Remoto
    """

    model = Publicacao
    serializer_class = PublicacaoSerializer


class PublicacaoCoreView(ApiCore):
    """
    CRUD de Membros Trabalho Remoto
    """

    model = Publicacao
    serializer_class = PublicacaoSerializer

    def confirmar_publicacao(self, request, *args, **kwargs):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda.",
            "status": status.HTTP_200_OK,
        }

        try:
            set_current_user(request.user)
            publicacao = self.get_object()
            publicacao.confirm_publication(
                publication_number=self.request.POST.get("numero_publicacao"),
                publication_date=DateUtils.str_to_date(
                    self.request.POST.get("data_publicacao")
                ),
                page=int(self.request.POST.get("vehicle_page") or 0),
            )
            rst.update(
                message="Publicação Confirmada ", status=status.HTTP_202_ACCEPTED
            )

        except Exception as e:
            rst.update(
                message="{}".format(e.args[0]), status=status.HTTP_400_BAD_REQUEST
            )

        return Response(rst, status=rst.get("status"))

    def enviar_publicacao(self, request, *args, **kwargs):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda.",
            "status": status.HTTP_200_OK,
        }

        try:
            set_current_user(request.user)
            publicacao = self.get_object()
            publicacao.sent_to_publication(
                int(self.request.POST.get("veiculo_publicacao") or 0)
            )
            rst.update(message="Publicação Enviada ", status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            rst.update(
                message="{}".format(e.args[0]), status=status.HTTP_400_BAD_REQUEST
            )

        return Response(rst, status=rst.get("status"))


class VeiculoPublicacaoListView(ListBaseView):
    """
    View de Membros Trabalho Remoto
    """

    model = Choice
    serializer_class = VeiculoPublicacaoSerializer
    queryset = Choice.objects.filter(name="VEICULO_PUBLICACAO", active=True)


class PublicationViewSet(BaseViewSet):
    """
    View das publicações
    """

    permission_classes = [IsAuthenticated]
    queryset = Publicacao.objects.filter()
    authentication_classes = [MultiAuthentication]
    serializer_class = PublicationSerializer
    full_text_index = ("cache_unicode__icontains",)

    def get_queryset(self):
        return self.queryset.filter()

    def get(self, request, *args, **kwargs):
        """
        Retorno das publicações
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
        keyword = request.query_params.get("keyword")
        per_page = int(request.query_params.get("per_page", 10))
        page = request.query_params.get("page")

        if keyword:
            queryset = Publicacao.objects.filter(cache_unicode__icontains=keyword)

        if page is not None:
            paginator = PageNumberPagination()
            paginator.page_size = per_page
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = self.get_serializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
