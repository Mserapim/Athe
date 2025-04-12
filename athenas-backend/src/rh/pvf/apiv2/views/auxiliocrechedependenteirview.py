from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from rest_framework.permissions import IsAuthenticated
from rh.pvf.apiv2.serializers.auxiliocrechedependenteirserializers import (
    PVFSolicitacaoCreteAuxCrecheDepenIRSerializer,
)
from rest_framework.response import Response
from rh.dayoff.const import *
from rh.pvf.models import PVFSolicitacaoAuxilioCrecheDepenIR
from rest_framework.decorators import action
from contrib.middleware import set_current_user
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import GenericViewSet


class PVFSolicitacaoCreteAuxCrecheDepenIRView(ApiCore):
    """
    View da criação da solicitação de auxilio creche e depedente de IR
    """

    permission_classes = [IsAuthenticated]
    queryset = PVFSolicitacaoAuxilioCrecheDepenIR.objects.filter()
    serializer_class = PVFSolicitacaoCreteAuxCrecheDepenIRSerializer

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "pessoa_familia_id": {"type": "integer"},
                    "anexo_id": {"type": "integer"},
                    "dependente_aux_creche": {"type": "bool"},
                    "dependente_ir": {"type": "bool"},
                    "capacidade": {"type": "integer"},
                    "tipo_parentesco": {"type": "integer"},
                    "dependente_tipo": {"type": "integer"},
                    "observacao": {"type": "string"},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação"""
        return self.create(request, *args, **kwargs)

    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().criar(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFSolicitacaoReenvioAuxCrecheDepenIRView(GenericViewSet):
    """
    View da reenvio da solicitação de auxilio creche e depedente de IR
    """

    permission_classes = [IsAuthenticated]
    queryset = PVFSolicitacaoAuxilioCrecheDepenIR.objects.filter()
    serializer_class = PVFSolicitacaoCreteAuxCrecheDepenIRSerializer

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "pessoa_familia_id": {"type": "integer"},
                    "anexo_id": {"type": "integer"},
                    "dependente_aux_creche": {"type": "bool"},
                    "dependente_ir": {"type": "bool"},
                    "capacidade": {"type": "integer"},
                    "tipo_parentesco": {"type": "integer"},
                    "dependente_tipo": {"type": "integer"},
                    "observacao": {"type": "string"},
                },
            },
        },
    )
    @action(detail=False, methods=["POST"])
    def reenviar(self, request, pk=None):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().reenviar(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFSolicitacaoReenvioAuxCrecheDepenIRDetalhes(ApiDetailView):
    """
    View dos detalhes da solicitação de auxilio creche de dependente de IR
    """

    model = PVFSolicitacaoAuxilioCrecheDepenIR
    serializer_class = PVFSolicitacaoCreteAuxCrecheDepenIRSerializer
