from rh.apiv2.serializers.lotacao import (
    ComarcaSerializer,
    LotacaoSerializer,
    ServidorLotacaoZonaEleitoralSerializer,
    WorkplaceSerializer,
)
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from auth.backend import CustomTokenJWTAuthentication, MultiAuthentication
from rest_framework.generics import ListAPIView
from apiv2.pagination import CustomPagination
from rh.models import Comarca, ServidorLotacao
from rest_framework.response import Response
from apiv2.baseviews import ListBaseView
from apiv2.baseviews import BaseViewSet
from rh.models import Lotacao
from django.contrib.auth.models import User
from rest_framework import status


from contrib.utils import DateUtils, getLogger

log = getLogger(__name__)


class LotacaoListView(ListBaseView):
    queryset = Lotacao.objects.all().order_by("nome")
    serializer_class = LotacaoSerializer
    full_text_index = (
        "nome__unaccent__icontains",
        "descricao__unaccent__icontains",
        "abreviacao",
        "sigla",
    )


class ComarcaLotacaoView(ListBaseView):
    queryset = Comarca.objects.all().order_by("nome")
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination
    serializer_class = ComarcaSerializer


class WorkplaceViewSet(BaseViewSet):
    """
    View das Lotações
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiAuthentication]
    queryset = Lotacao.objects.filter(ativo=True)
    serializer_class = WorkplaceSerializer
    full_text_index = ("nome__unaccent__icontains", "id__iexact")

    def get_queryset(self):
        return self.queryset.filter(electoral_zone=False)

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


class ServidorLotacaoZonaEleitoralView(ListBaseView):
    """
    View das lotações de zonas eleitorais do servidor
    """

    model = ServidorLotacao
    authentication_classes = [MultiAuthentication]
    serializer_class = ServidorLotacaoZonaEleitoralSerializer
    full_text_index = ("lotacao__nome__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="login", description="login do servidor ", type=int),
            OpenApiParameter(name="data_inicio", description="data início", type=str),
            OpenApiParameter(name="data_fim", description="data fim", type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View das lotações de zonas eleitorais do servidor
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        login = request.GET.get("login", None)
        dt_inicio = request.GET.get("data_inicio", None)
        dt_fim = request.GET.get("data_fim", None)
        if login is None:
            return Response(
                {"erro": "A requisição deve enviar o parâmetro login"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if dt_inicio is None or dt_fim is None:
            return Response(
                {
                    "erro": "A requisição deve enviar os parâmetros data_inicio e data_fim"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super(ServidorLotacaoZonaEleitoralView, self).list(request)

    def get_queryset(self):
        usuario = User.objects.get(username=self.request.GET.get("login"))
        dt_inicio = DateUtils.str_to_date(
            self.request.GET.get("data_inicio"), format="%Y-%m-%d"
        )
        dt_fim = DateUtils.str_to_date(
            self.request.GET.get("data_fim"), format="%Y-%m-%d"
        )

        queryset = self.model.objects.filter(
            servidor=usuario.servidor,
            data_vigencia_inicio__lte=dt_fim,
            data_vigencia_fim__gte=dt_inicio,
            lotacao__electoral_zone=True,
        )
        return queryset
