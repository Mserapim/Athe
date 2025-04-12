from apiv2.utils import response_api_view
from rh.pvf.apiv2.serializers.calendarserializers import (
    PVFCalendarSerializer,
    PVFEmployeeTeamSerializer,
    PVFEventTypeSerializer,
)
from rh.models import Servidor
from standard.models import Choice
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rest_framework.views import APIView
from rh.pvf.apiv2.utils.calendar import get_data_calendar
from drf_spectacular.utils import OpenApiParameter, extend_schema
from apiv2.baseviews import ListBaseView
from rest_framework.response import Response
from rh.pvf.apiv2.utils.base import get_workers
from rh.models import Servidor


class PVFCalendarView(ListBaseView):
    """
    View dos eventos(calendário) VDF
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    description_param = "Valores múltiplos[]"

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="keyword", type=str),
            OpenApiParameter(name="year", description="Ano", type=int),
            OpenApiParameter(name="month", description="Mês", type=int),
            OpenApiParameter(
                name="employee_ids",
                description="Ids Servidores " + description_param,
                type=int,
            ),
            OpenApiParameter(
                name="event_type_ids",
                description="Tipos de eventos " + description_param,
                type=int,
            ),
            OpenApiParameter(
                name="group_ids",
                description="Grupo de eventos " + description_param,
                type=int,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        employee = Servidor.objects.get(user=self.request.user)
        params = self.request.query_params
        data = get_data_calendar(employee, params)
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = PVFCalendarSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = PVFCalendarSerializer(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFEmployeeTeamView(ListBaseView):
    """
    View que retorna equipe do servidor na agenda
    """

    queryset = Servidor.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFEmployeeTeamSerializer
    full_text_index = ("pessoa_fisica__nome__unaccent__icontains",)

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        workers = get_workers(employee)
        querset = self.queryset.filter(pk__in=workers)
        return querset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada do time do responsável.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFEventTypeView(ListBaseView):
    """
    View que retorna a lista dos tipos de eventos
    """

    queryset = Choice.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFEventTypeSerializer

    def get_queryset(self):
        querset = self.queryset.filter(
            name__in=[
                "SUB_CONFIGURATION_CHOICE",
                "TYPE_OF_LICENSE",
                "GENERIC_EVENT_TYPES",
            ]
        ).order_by("label")
        return querset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET<br>
        Lista montada com as configurações de parâmetros (GENERIC_EVENT_TYPES, TYPE_OF_LICENSE, SUB_CONFIGURATION_CHOICE)
        """
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada do time do responsável.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)
