from apiv2.baseviews import BaseViewSet
from apiv2.utils import response_api_view
from contrib.middleware import set_current_user
from rh.gfp.models import (
    HorizontalProgressionConfig,
    MovimentacaoProgressao,
    ProgressionDocument,
)
from rh.pvf.apiv2.serializers.baseserializers import *
from rh.models import Servidor
from auth.permissions.vdf.permissions import IsPermissionVDF
from rh.pvf.apiv2.serializers.progressionserializers import *
from rh.pvf.apiv2.utils.progression import get_employee_schooling, get_possible_levels
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.pvf.models import PRProgressionHDocument, PortalRequestProgressionH
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rh.pvf.const import *


class PVFMovProgressionHViewSet(BaseRequestViewSet):
    """
    View da movimentação de progressão
    """

    queryset = MovimentacaoProgressao.objects.filter()
    serializer_class = PVFMovProgressionHSerializers

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = (
            self.queryset.filter(
                data_fim_vigencia=None,
                servidor__ativo=True,
                expected_date__isnull=False,
                ativo=True,
                movimentacao_posse__servidor=employee,
            )
            .exclude(referencia_nivel2d__cargos_estrutura__cargo__tipo_lei_cargo="CM")
            .order_by("expected_date", "movimentacao_posse__servidor")
            .distinct()
        )
        return self.filter_queryset(queryset)


class PVFConfigProgressionHViewSet(BaseRequestViewSet):
    """
    View da config progressão horizontal
    """

    queryset = HorizontalProgressionConfig.objects.filter()
    serializer_class = PVFConfigProgressionHSerializers

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        employee_schooling = get_employee_schooling(employee)
        possible_levels = get_possible_levels(employee)
        queryset = self.queryset.filter(
            schooling=employee_schooling, target_level__in=possible_levels
        )
        return self.filter_queryset(queryset)


class PVFDocumentProgressionHViewSet(BaseViewSet):
    """
    View de documento de progressão horizontal
    """

    queryset = PRProgressionHDocument.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFDocumentProgressionHSerializers

    def get_queryset(self):
        return self.queryset.filter()

    def post(self, request, *args, **kwargs):
        """Cria um documento de progressão horizontal"""
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Atualiza um documento de progressão horizontal"""
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Deleta um documento de progressão horizontal"""
        return self.exclude(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        set_current_user(request.user)
        serializer = self.get_serializer(data=request.data)
        response = serializer.perform_create()
        return Response(response, status=response["code"])

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        response = serializer.perform_update(instance)
        return Response(response, status=response["code"])

    def exclude(self, request, *args, **kwargs):
        set_current_user(request.user)
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PVFDocumentProgressionVViewSet(BaseViewSet):
    """
    View de documento de progressão vertical
    """

    queryset = ProgressionDocument.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFDocumentProgressionVSerializers

    def get_queryset(self):
        return self.queryset.filter()

    def post(self, request, *args, **kwargs):
        """Cria um documento de progressão vertical"""
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Atualiza um documento de progressão vertical"""
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Deleta um documento de progressão vertical"""
        return self.exclude(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "request_id": {"type": "integer"},
                    "description": {"type": "string"},
                    "attachment": {"type": "integer"},
                },
            },
        },
    )
    def create(self, request, *args, **kwargs):
        set_current_user(request.user)
        serializer = self.get_serializer(data=request.data)
        response = serializer.perform_create()
        return Response(response, status=response["code"])

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "request_id": {"type": "integer"},
                    "description": {"type": "string"},
                    "attachment": {"type": "integer"},
                },
            },
        },
    )
    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        response = serializer.perform_update(instance)
        return Response(response, status=response["code"])

    def exclude(self, request, *args, **kwargs):
        set_current_user(request.user)
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PVFListDocumentProgressionView(BaseRequestViewSet):
    """
    View de documento de progressão horizontal
    """

    queryset = PRProgressionHDocument.objects.filter()
    serializer_class = PVFDocumentProgressionHSerializers

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    @action(detail=True, methods=["GET"])
    def request_document_progressions(self, request, pk=None):
        queryset = self.queryset.filter(pr_progression_h__pk=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFListDocumentProgressionVerticalView(BaseRequestViewSet):
    """
    View de documento de progressão vertical
    """

    queryset = ProgressionDocument.objects.filter()
    serializer_class = PVFDocumentProgressionVSerializers

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    @action(detail=True, methods=["GET"])
    def request_document_progressions(self, request, pk=None):
        queryset = self.queryset.filter(progression__portal_request_progression=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFCreateRequestProgressionHViewSet(GenericViewSet):
    """
    View da criação da solicitação de progressão horizontal
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRequestProgressionH.objects.filter()
    serializer_class = PVFSendProgressionHViewSetSerializer

    def get_queryset(self):
        return self.queryset.filter()

    def post(self, request, *args, **kwargs):
        """Cria uma solicitação de progressão horizontal"""
        return self.create(request, *args, **kwargs)

    def put(self, request, pk, *args, **kwargs):
        """Atualiza uma solicitação de progressão horizontal"""
        return self.update(request, pk, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "progression": {"type": "integer"},
                    "config": {"type": "integer"},
                    "documents": {"type": "[{name:str,attachment_id:integer}]"},
                },
            },
        },
    )
    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, ValidationError):
            custom_response_data = {"success": False, "message": str(exc.detail)}
            response.data = custom_response_data
            response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().update(pk, data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFSendProgressionHViewSet(GenericViewSet):
    """
    View do envio da solicitação de progressão horizontal
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRequestProgressionH.objects.filter()
    serializer_class = PVFSendProgressionHViewSetSerializer

    @action(detail=False, methods=["POST"])
    def send(self, request, pk=None):
        set_current_user(request.user)
        serializer_data = self.serializer_class().send(pk)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)
