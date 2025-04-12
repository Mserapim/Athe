from apiv2.baseviews import ListBaseView
from apiv2.utils import response_api_view
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from drf_spectacular.utils import extend_schema
from rh.models import MovimentacaoTeletrabalho, Servidor
from contrib.middleware import set_current_user
from rest_framework import status
from rest_framework.response import Response
from rh.pvf.apiv2.serializers.baseserializers import PVFConfigTypeSerializer
from rh.pvf.apiv2.serializers.sendteleworkserializers import PVFSendTeleworkSerializer
from rh.pvf.models import (
    PVFCancelamentoTeletrabalho,
    PortalCancelSchedule,
    SendingTelework,
)
from rh.dayoff.models import Usufruct
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.pvf.apiv2.serializers.cancelserializers import (
    PVFCancelScheduleSerializers,
    PVFCancelUsufructSerializer,
    PVFCancelamentoTeletrabalhoSerializer,
    PVFRequestCancelSerializer,
)
from rh.dayoff.const import USU_HOMOLOGATED, USU_SOLD, USU_ENJOYING, USU_ENJOYED
from rh.pvf.apiv2.utils.base import cancel_usufructs
from standard.models import Choice
from rh.pvf.models import PortalRequest
from datetime import datetime, timedelta
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action


class PVFCancelScheduleViewSet(GenericViewSet):
    """
    View da solicitação de cancelamento da programação
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalCancelSchedule.objects.filter()
    serializer_class = PVFCancelScheduleSerializers

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee)
        return queryset

    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação de cancelamento de programação"""
        return self.create(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "usufruct_id": {"type": "integer"},
                    "observation": {"type": "string"},
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


class PVFRequestCancelViewSet(GenericViewSet):
    """
    View que realizar o cancelamento da solicitação
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRequest.objects.filter()
    serializer_class = PVFRequestCancelSerializer

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        set_current_user(request.user)
        req = self.queryset.filter(pk=pk).first()
        serializer_data = self.serializer_class().cancel(req)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFCancelUsufrctViewSet(BaseRequestViewSet):
    """
    View que retorna os usufrutos que podem ser cancelados
    """

    queryset = Usufruct.objects.filter()
    serializer_class = PVFCancelUsufructSerializer

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        if employee.type_by_possession in ["MBR", "MEL", "MEC"]:
            amount_past_days = Choice.objects.filter(
                name="VDF_AMOUNT_PAST_DAYS_FOR_CANCEL_AND_RETIFICATION_MEMBER"
            ).first()
        else:
            amount_past_days = Choice.objects.filter(
                name="VDF_AMOUNT_PAST_DAYS_FOR_CANCEL_AND_RETIFICATION"
            ).first()
        qtd_days = 0
        if amount_past_days:
            qtd_days = amount_past_days.value
        queryset = self.queryset.filter(
            activity__acquisition_period__employee=employee,
            status__in=[USU_HOMOLOGATED, USU_SOLD, USU_ENJOYING, USU_ENJOYED],
            activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=cancel_usufructs(),
            start_date__gte=(datetime.today().date() - timedelta(days=qtd_days)),
        )
        return self.filter_queryset(queryset)


class PVFCancelamentoTeletrabalhoView(GenericViewSet):
    """
    View da solicitação de cancelamento de teletrabalho
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PVFCancelamentoTeletrabalho.objects.filter()
    serializer_class = PVFCancelamentoTeletrabalhoSerializer

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee)
        return queryset

    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação de cancelamento"""
        return self.create(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "request_ids": {"type": "[]"},
                    "observation": {"type": "string"},
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


class PVFListaCancelamentoTeletrabalhoView(BaseRequestViewSet):
    """
    View da lista de teletrabalhos
    """

    queryset = SendingTelework.objects.filter()
    serializer_class = PVFSendTeleworkSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    @action(detail=True, methods=["GET"])
    def solicitacoes_teletrabalho(self, request, pk=None):
        queryset = self.queryset.filter(pvf_envios_teletrabalho=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFConfigTipoCancelamentoView(BaseRequestViewSet):
    """
    View da config dos tipos de cancelamentos
    """

    queryset = Choice.objects.all()
    serializer_class = PVFConfigTypeSerializer

    def get_queryset(self):
        return self.queryset.filter(name="TIPOS_CANCELAMENTO")
