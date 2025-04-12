from apiv2.baseviews import ListBaseView
from apiv2.utils import response_api_view
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from drf_spectacular.utils import extend_schema
from rh.models import (
    ConfigPeriodoCumulativoSubstituicao,
    MovimentacaoSubstituicao,
    Servidor,
)
from contrib.middleware import set_current_user
from rest_framework import status
from rest_framework.response import Response
from rh.pvf.apiv2.serializers.baseserializers import (
    PVFMinhasSubstituicoesSerializer,
    PVFVendaSubstituicoesSerializer,
)
from rh.pvf.apiv2.serializers.exerciciocumulativoserializers import (
    PVFDiasConsolidadosSerializer,
    PVFExercicioCumulativoSerializers,
    PVFIndefirExercicioCumulativoeSerializer,
    PVFSubstituicaoConfigPeridoVendaSerializers,
)
from rh.pvf.apiv2.utils.exerciciocumulativo import calc_dias_consolidados
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.pvf.models import PVFExercicioCumulativo
from rh.dayoff.const import *
from rest_framework.decorators import action
from drf_spectacular.utils import OpenApiParameter, extend_schema


class PVFExercicioCumulativoView(GenericViewSet):
    """
    View da solicitação de venda de exercicio cumulativo
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PVFExercicioCumulativo.objects.filter()
    serializer_class = PVFExercicioCumulativoSerializers

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee)
        return queryset

    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação de venda de exercicio cumulativo"""
        return self.create(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "substituicoes_ids": {"type": "[]"},
                    "observacao": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFEnviarExercicioCumulativoView(GenericViewSet):
    """
    View da envio da solicitação de venda de exercicio cumulativo
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PVFExercicioCumulativo.objects.filter()
    serializer_class = PVFExercicioCumulativoSerializers

    @action(detail=False, methods=["POST"])
    def send(self, request, pk=None):
        set_current_user(request.user)
        serializer_data = self.serializer_class().send(request.data, pk)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFListaSubstiuicaoView(BaseRequestViewSet):
    """
    View da lista das substituções da solicitacao de venda de exercicio cumulativo
    """

    queryset = MovimentacaoSubstituicao.objects.filter()
    serializer_class = PVFVendaSubstituicoesSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    @action(detail=True, methods=["GET"])
    def lista_substituicoes(self, request, pk=None):
        queryset = self.queryset.filter(pvf_exercicio_cumulativos__id=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFSubstituicaoConfigPeridoVendaView(ListBaseView):
    """
    View da lista das configuração de período de venda de exercicio cumulativo
    """

    queryset = ConfigPeriodoCumulativoSubstituicao.objects.filter()
    serializer_class = PVFSubstituicaoConfigPeridoVendaSerializers

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFIndeferirExercicioCumulativoView(GenericViewSet):
    """
    View para realiza a operção de indeferir subsituição de exercicio cumulativo
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = MovimentacaoSubstituicao.objects.filter()
    serializer_class = PVFIndefirExercicioCumulativoeSerializer

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"observation": {"type": "string"}},
            },
        },
    )
    @action(detail=True, methods=["POST"])
    def indeferir(self, request, pk=None):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().indeferir(data, pk)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFDiasConsolidadoView(BaseRequestViewSet):
    """
    View que retorna quantos dias serão consolidados da solicitação de exercicio cumulativo
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @action(detail=True, methods=["GET"])
    def dias_consolidados(self, request, pk=None):
        solicitacao = PVFExercicioCumulativo.objects.get(pk=pk)
        dias_cons = calc_dias_consolidados(solicitacao)
        data = {"dias_consolidados": dias_cons}
        data = PVFDiasConsolidadosSerializer(data).data
        return Response(data)
