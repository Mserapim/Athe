import datetime
from contrib.utils import DateUtils, employee_from_user, getLogger, person_from_user
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.db.models import Q
from apiv2.baseviews import BaseViewSet, ListBaseView
from apiv2.utils import response_api_view
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rest_framework.response import Response
from contrib.middleware import set_current_user
from rh.dayoff.const import *
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rh.models import Servidor
from rh.pvf.apiv2.serializers.serverdutyserializers import PVFShiftManagerSerializer
from rh.pvf.apiv2.utils.base import convert_data
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.pvf.const import GROUP_SERVER
from rh.pvf.models import ShiftManager
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView


log = getLogger(__name__)


class PVFServeDutyViewSet(RetrieveUpdateDestroyAPIView):
    """
    View das escalas de plantões servidores
    """

    queryset = ShiftManager.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFShiftManagerSerializer
    full_text_index = (
        "employee__pessoa_fisica__nome__unaccent__icontains",
        "employee__pessoa_fisica__social_name__unaccent__icontains",
    )

    def put(self, request, *args, **kwargs):
        """Atualiza uma escala de plantão"""
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Deleta uma escala de plantão"""
        return self.exclude(request, *args, **kwargs)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        data = convert_data(request.data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        response = serializer.perform_update(instance=instance)
        return Response(response, status=response["code"])

    def exclude(self, request, *args, **kwargs):
        instance = self.get_object()
        response = self.serializer_class().perform_delete(instance)
        return Response(response, status=response["code"])


class PVFCriarListarPlantoesServidores(ListBaseView, CreateAPIView):

    queryset = ShiftManager.objects.filter()
    permission_classes = [IsAuthenticated]
    serializer_class = PVFShiftManagerSerializer
    full_text_index = (
        "employee__pessoa_fisica__nome__unaccent__icontains",
        "employee__pessoa_fisica__social_name__unaccent__icontains",
        "employee__matricula__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="start_date", description="Data de início", type=str),
            OpenApiParameter(name="end_date", description="Data fim", type=str),
            OpenApiParameter(
                name="tipo_plantao[]",
                description="Lista de ids do tipo de plantão",
                type=int,
            ),
            OpenApiParameter(
                name="comarca_id[]", description="Lista de ids das comarcas", type=int
            ),
            OpenApiParameter(name="lotacao_id", description="Id da lotação", type=int),
            OpenApiParameter(
                name="cadastrado_por", description="Cadastrado por", type=str
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """Retorna as escalas"""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Cria uma nova escala de plantão"""
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        set_current_user(request.user)
        data = convert_data(request.data)
        serializer = self.get_serializer(data=data)
        response = serializer.perform_create()
        return Response(response, status=response["code"])

    def get_queryset(self):
        user = self.request.user
        servidor = Servidor.objects.get(user=user)

        if (
            Group.objects.get(name=GROUP_SERVER) in user.groups.all()
            or ShiftManager.objects.filter(owner=servidor).exists()
        ):
            queryset = ShiftManager.objects.all()
        else:
            queryset = ShiftManager.objects.none()

        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        keyword = self.request.query_params.get("keyword", None)
        tipo_plantao_lista = self.request.query_params.getlist("tipo_plantao[]", None)
        comarca_id_lista = self.request.query_params.getlist("comarca_id[]", None)
        lotacao_id = self.request.query_params.get("lotacao_id", None)
        cadastrado_por = self.request.query_params.get("cadastrado_por", None)

        if keyword:
            queryset = queryset.filter(
                Q(employee__pessoa_fisica__nome__unaccent__icontains=keyword)
                | Q(employee__pessoa_fisica__social_name__unaccent__icontains=keyword)
                | Q(employee__matricula__icontains=keyword)
            )
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            queryset = queryset.filter(end_date__gte=start_date)
        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(start_date__lte=end_date)
        if tipo_plantao_lista:
            queryset = queryset.filter(type_shift__in=tipo_plantao_lista)
        if comarca_id_lista:
            queryset = queryset.filter(
                workplace__localidade__comarca__in=comarca_id_lista
            )
        if lotacao_id:
            queryset = queryset.filter(workplace=lotacao_id)
        if cadastrado_por == "usuario_atual":
            queryset = queryset.filter(owner=servidor)

        list_queryset = list(queryset)
        status_filter = self.request.query_params.getlist("status[]")
        if status_filter:
            filtered_records = [
                record
                for record in list_queryset
                if str(record.get_status) in status_filter
            ]
            ids = [record.pk for record in filtered_records]
            queryset = queryset.filter(pk__in=ids)
        return queryset


class PVFRequestServeDutyViewSet(BaseRequestViewSet):
    """
    View do detail da escala de plantão servidores
    """

    queryset = ShiftManager.objects.filter()
    serializer_class = PVFShiftManagerSerializer
    full_text_index = (
        "employee__pessoa_fisica__nome__unaccent__icontains",
        "employee__pessoa_fisica__social_name__unaccent__icontains",
    )

    @action(detail=True, methods=["GET"])
    def request_server_shifts(self, request, pk=None):
        queryset = self.queryset.filter(server_duty__pk=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)
