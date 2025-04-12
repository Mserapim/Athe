from apiv2.utils import response_api_view
from rh.pvf.apiv2.serializers.absenceserializers import *
from rh.models import Servidor
from rh.pvf.const import *
from rh.pvf.apiv2.views.baseviews import PVFRequestView
from rh.pvf.apiv2.serializers.baseserializers import *
from rh.pvf.apiv2.filters import PVFApprovalRequestListFilterBackend
from django.db.models import Q
from rh.pvf.apiv2.utils.approval import query_approvals
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rh.pvf.apiv2.serializers.approvalserializers import (
    PVFRequestAuthorizeSerializer,
    PVFApprovalActionsSerializer,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rh.pvf.apiv2.utils.approval import acoes_aprovador
from contrib.middleware import set_current_user
from rest_framework import status
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rest_framework.decorators import action


class PVFWaitingApprovalViewSet(PVFRequestView):
    """
    View da tela aguardando aprovação
    """

    filter_backends = (PVFApprovalRequestListFilterBackend,)
    full_text_index = (
        "approver__pessoa_fisica__nome__unaccent__icontains",
        "employee__pessoa_fisica__nome__unaccent__icontains",
        "approver__matricula__icontains",
        "employee__matricula__icontains",
        "pk__iexact",
    )

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset

        query = query_approvals(queryset, employee)
        return self.filter_queryset(query)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="status[]", description="Situação", type={"type": "array"}
            ),
            OpenApiParameter(
                name="request_type[]",
                description="Tipo de solicitação",
                type={"type": "array"},
            ),
            OpenApiParameter(
                name="approvals[]", description="Aprovadores", type={"type": "array"}
            ),
            OpenApiParameter(
                name="employe_types[]",
                description="Tipo de Servidor",
                type={"type": "array"},
            ),
            OpenApiParameter(
                name="pending_request", description="Somente Pendências", type=bool
            ),
            OpenApiParameter(
                name="data_inicio", description="Data Início", type={"type": "date"}
            ),
            OpenApiParameter(
                name="data_fim", description="Data Fim", type={"type": "date"}
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """Retorna as solicitações"""
        return self.list(request, *args, **kwargs)

    def list(self, request):
        """
        Obtém a lista paginada.
        """
        queryset = self.order_queryset(self.get_queryset())
        exportar = request.GET.get("exportar", None)
        sincrono = request.GET.get("sincrono", False)
        if exportar:
            campos = request.GET.getlist("colunas[]", [])
            return self.exportar_arquivo(exportar, campos, sincrono, queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PVFApprovalActionsView(BaseRequestViewSet):
    """
    View das ações permitidas para aprovação da solicitação
    """

    # queryset = None
    serializer_class = PVFApprovalActionsSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    @action(detail=True, methods=["GET"])
    def actions(self, request, pk=None):
        employee = Servidor.objects.get(user=self.request.user)
        request = PortalRequest.objects.filter(pk=pk).first()
        data = sorted(acoes_aprovador(request, employee), key=lambda x: x["order"])
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = self.serializer_class(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        return response_api_view([])


class PVFRequestAuthorizeViewSet(GenericViewSet):
    """
    View para realiza as operações do fluxo de aprovação
    (deferir, indeferir, efetivar, cancelar, ciência e anotar)
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRequest.objects.filter()
    serializer_class = PVFRequestAuthorizeSerializer

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "observation": {"type": "string"},
                    "publication": {"type": "number"},
                    "anexos": {"type": "[]"},
                },
            },
        },
    )
    @action(detail=True, methods=["POST"])
    def authorize(self, request, pk=None):
        set_current_user(request.user)
        req = self.queryset.filter(pk=pk).first()
        data = request.data
        serializer_data = self.serializer_class().authorize(data, req)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)
