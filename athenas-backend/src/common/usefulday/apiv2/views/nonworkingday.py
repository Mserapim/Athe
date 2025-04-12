from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema

from django.db.models import Q
from common.usefulday.models import NonWorkingDay
from rh.models import Localidade
from standard.models import Choice

from common.usefulday.api.nonworkingday import CUNNonWorkingDay
from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView
from apiv2.pagination import CustomPagination
from auth.backend import CustomTokenJWTAuthentication
from common.usefulday.apiv2.serializers.nonworkingday import (
    NonWorkingDaySerializer,
    DiasUteisSerializer,
)
from rh.apiv2.serializers.localidade import LocationsSerializer
from contrib.middleware import set_current_user
from rh.pvf.apiv2.utils.base import convert_data

from contrib.utils import getLogger

log = getLogger(__name__)


class NonWorkingDayView(ListBaseView):
    """
    View de NonWorkingDay
    """

    queryset = NonWorkingDay.objects.all().order_by("-start_date")
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomTokenJWTAuthentication]
    pagination_class = CustomPagination
    serializer_class = NonWorkingDaySerializer
    full_text_index = ("description__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="year", description="Ano", type=int),
            OpenApiParameter(name="abrangency", description="Abrangência", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Obtém a lista paginada de NonWorkingDay.
        """
        queryset = self.filter_queryset(self.get_queryset())
        params = self.request.query_params
        if params:
            year = params.get("year", None)
            abrangency = params.get("abrangency", None)
            if year and len(year) == 4:
                queryset = queryset.filter(start_date__year=year)
            if abrangency:
                queryset = queryset.filter(abrangency=abrangency)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DiasUteisView(ListBaseView):
    """
    View de NonWorkingDay
    """

    queryset = NonWorkingDay.objects.all().order_by("-start_date")
    permission_classes = [IsAuthenticated]
    serializer_class = DiasUteisSerializer
    full_text_index = ("description__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="abrangencia[]", description="Abrangência", type=int),
            OpenApiParameter(name="tipo[]", description="Tipo", type=int),
            OpenApiParameter(name="ano", description="Ano", type=int),
            OpenApiParameter(name="mes", description="Mês", type=int),
            OpenApiParameter(name="data_inicio", description="Data início", type=str),
            OpenApiParameter(name="data_fim", description="Data Fim", type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = NonWorkingDay.objects.all()
        palavra_chave = self.request.query_params.get("keyword", None)
        abrangencia_lista = self.request.query_params.getlist("abrangencia[]", None)
        tipo_lista = self.request.query_params.getlist("tipo[]", None)
        ano = self.request.query_params.get("ano", None)
        mes = self.request.query_params.get("mes", None)
        data_inicio = self.request.query_params.get("data_inicio", None)
        data_fim = self.request.query_params.get("data_fim", None)

        if palavra_chave:
            queryset = queryset.filter(
                Q(description__unaccent__icontains=palavra_chave)
            )
        if abrangencia_lista:
            queryset = queryset.filter(abrangency__in=abrangencia_lista)
        if tipo_lista:
            queryset = queryset.filter(kind__in=tipo_lista)
        if ano:
            queryset = queryset.filter(start_date__year=ano)
        if mes:
            queryset = queryset.filter(start_date__month=mes)
        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            queryset = queryset.filter(
                Q(
                    start_date__gte=data_inicio,
                    start_date__lte=data_fim,
                    end_date__isnull=True,
                )
                | Q(start_date__gte=data_inicio, end_date__lte=data_fim)
            )
        elif data_inicio:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            queryset = queryset.filter(end_date__gte=data_inicio)
        elif data_fim:
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            queryset = queryset.filter(start_date__lte=data_fim)

        return queryset


class DiasUteisDetailView(ApiDetailView):
    """
    View de detalhes de Servico
    """

    model = NonWorkingDay
    serializer_class = DiasUteisSerializer


class DiasUteisApicoreView(ApiCore):
    """
    View de criar, editar e apagar o Dia Útil
    """

    model = NonWorkingDay
    serializer_class = DiasUteisSerializer
    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
        "copiar": "copiar",
    }

    def copiar(self, request, *args, **kwargs):
        rst = {
            "success": False,
            "message": "Nada feito ainda!",
            "code": 200,
        }

        set_current_user(request.user)
        try:
            NonWorkingDay.copy(request.data)
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Ação realizada com sucesso.")

        return Response(rst, status=rst["code"])


class LocalidadeSelecionadaDiaUtilAPIList(ListBaseView):
    """
    View para listar as Localidades de um Dia Útil
    """

    model = Localidade
    serializer_class = LocationsSerializer
    full_text_index = ("nome__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="dia_util_id", description="ID do dia útil", type=int
            ),
        ]
    )
    def get_queryset(self):
        dia_util_id = self.request.GET.get("dia_util_id")

        try:
            dia_util = NonWorkingDay.objects.get(pk=dia_util_id)
            return dia_util.places.all()
        except:
            return []


class DiasUteisFiltroAnosACopiarView(ListBaseView):
    """
    View da lista de anos de dias úteis para a tela de copiar
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": NonWorkingDay.get_year_list(),
        }

        return Response(res)


class DiasUteisFiltroTiposACopiarView(ListBaseView):
    """
    View da lista de tipos de dias úteis para a tela de copiar
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": Choice.objects.filter(app_label="usefulday", name="KIND")
            .order_by("label")
            .values("value", "label"),
        }

        return Response(res)
