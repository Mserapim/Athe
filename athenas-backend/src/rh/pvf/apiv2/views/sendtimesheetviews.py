from django.shortcuts import get_object_or_404
from apiv2.baseviews import ListBaseView, BaseViewSet
from apiv2.utils import response_api_view
from rh.models import Servidor
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rh.pvf.apiv2.filters import PVFListaJustificativasFilter
from rh.pvf.apiv2.serializers.sendtimesheetserializers import (
    PVFFolhaPontoAfastamentosSerializer,
    PVFJustificationItensSerializer,
    PVFPendingTimeSheetSerializer,
    PVFPointJustificationSerializer,
    PVFReferenceTimeeSheetSerializer,
    PVFSendTimeSheetSerializer,
)
from apiv2.baseviews import ListBaseView
from rest_framework.response import Response
from rh.models import Servidor
from rh.pvf.apiv2.utils.timesheet import (
    envio_pendente_folha_ponto,
    get_reference_timesheet,
    get_data_type_by_possession_access,
    pending,
)
from rh.pvf.apiv2.utils.telework import is_workplan
from rh.dayoff.const import *
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.pvf.const import (
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
    STS_EFFECTIVE,
    STS_REJECTED,
)
from rh.pvf.models import PortalRequest, SendingTimeSheet
from standard.models import JustificationItem
from rh.pvf.models import PointJustification
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from contrib.middleware import set_current_user
from rest_framework import status
from rh.pvf.apiv2.utils.base import formart_date_str
from django.db.models.query_utils import Q


class PVFReferenceTimeSheetView(ListBaseView):
    """
    View da lista de referências disponiveis para realizar os envios folha ponto
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFReferenceTimeeSheetSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista de referências disponiveis para realizar os envios folha ponto pra que está em teletrabalho
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        employee = Servidor.objects.get(user=self.request.user)
        data = get_reference_timesheet(employee)
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = self.serializer_class(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = self.serializer_class(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFJustificationItensView(ListBaseView):
    """
    View das configs de justificativas do folha ponto
    """

    queryset = JustificationItem.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFJustificationItensSerializer

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        list_pks = get_data_type_by_possession_access(employee.type_by_possession)
        querset = self.queryset.filter(pk__in=list_pks)
        return querset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista das configs de justificativas do folha ponto
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        paginated_data = self.paginate_queryset(page)
        if paginated_data is not None:
            data_serializer = self.serializer_class(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = self.serializer_class(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFPointJustificationViewSet(BaseViewSet):
    """
    View das justificativas do folha ponto
    """

    queryset = PointJustification.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFPointJustificationSerializer

    def get_queryset(self):
        return self.queryset.filter()

    def post(self, request, *args, **kwargs):
        """Cria uma nova justificativa folha ponto"""
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Atualiza uma justificativa folha ponto"""
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Deleta uma justificativa folha ponto"""
        return self.exclude(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = self.convert_data(request.data)
        serializer = self.get_serializer(data=data)
        response = serializer.perform_create()
        return Response(response, status=response["code"])

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        data = self.convert_data(request.data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        response = serializer.perform_update(instance)
        return Response(response, status=response["code"])

    def exclude(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def convert_data(self, data):
        """
        Converte os dados recebidos no objeto 'data' para o formato esperado.
        Realiza as transformações necessárias nos dados fornecidos, garantindo que estejam
        corretamente formatados de acordo com as especificações definidas pela aplicação.
        Args:
            request (Request): O objeto 'data' contendo os dados a serem convertidos.
        Returns:
        dict: Os dados convertidos para o formato esperado.
        """
        if data.get("number_hours") != None:
            data["start_date"] = formart_date_str(
                data["start_date"], formart="%Y-%m-%d"
            )
            data["end_date"] = data["start_date"]
        else:
            data["number_hours"] = "00:00"
            data["start_date"] = formart_date_str(
                data["start_date"], formart="%Y-%m-%d"
            )
            data["end_date"] = formart_date_str(data["end_date"], formart="%Y-%m-%d")
        return data


class PVFListPointJustificationView(BaseRequestViewSet):
    """
    View da lista de justificativas do folha ponto
    """

    queryset = PointJustification.objects.filter()
    serializer_class = PVFPointJustificationSerializer
    filter_backends = (PVFListaJustificativasFilter,)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="cancelado", description="cancelado", type=bool),
        ]
    )
    @action(detail=True, methods=["GET"])
    def request_justifications(self, request, pk=None):
        queryset = self.queryset.filter(request__pk=pk)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFCreateSendingTimeSheetViewSet(GenericViewSet):
    """
    View da criação da solicitação de Folha Ponto
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = SendingTimeSheet.objects.filter()
    serializer_class = PVFSendTimeSheetSerializer

    def get_queryset(self):
        return self.queryset.filter()

    def post(self, request, *args, **kwargs):
        """Cria um novo envio do teletrabalho"""
        return self.create(request, *args, **kwargs)

    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFSendingTimeSheetViewSet(GenericViewSet):
    """
    View da envio da solicitação de Folha Ponto
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = SendingTimeSheet.objects.filter()
    serializer_class = PVFSendTimeSheetSerializer

    @action(detail=False, methods=["POST"])
    def send(self, request, pk=None):
        set_current_user(request.user)
        serializer_data = self.serializer_class().send(pk)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFPendingTimeSheetView(BaseRequestViewSet):
    """
    View da lista de pendências do folha ponto
    """

    serializer_class = PVFPendingTimeSheetSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    @action(detail=True, methods=["GET"])
    def request_pendencies(self, request, pk=None):
        data = pending(pk)
        page = self.paginate_queryset(data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(data, many=True)
        return response_api_view(serializer.data)


class PVFEnvioPedenteFolhaPontoView(ListBaseView):
    """
    View que retorna se tem folha ponto criado e pendente de envio
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    def get(self, request, *args, **kwargs):
        """
        Informações do envio folha ponto
        """
        servidor = Servidor.objects.get(user=self.request.user)
        set_current_user(request.user)
        dados = {}
        folha_ponto_pendente, folha_ponto_id = envio_pendente_folha_ponto(servidor)
        dados.update(
            {
                "timesheet_pending": folha_ponto_pendente,
                "timesheet_id": folha_ponto_id,
                "active_workplan": is_workplan(servidor),
            }
        )
        return Response(dados)


class PVFFolhaPontoAfastamentoView(ListBaseView):
    """
    View das solicitações de afastamentos abertos que não foram efetivadas
    """

    queryset = PortalRequest.objects.filter()
    serializer_class = PVFFolhaPontoAfastamentosSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="id", description="id da solicitação folha ponto", type=int
            ),
            OpenApiParameter(
                name="situação", description="situação da solicitação", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista das solicitações que geram afastamento na referêcia do folha ponto
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        id_solicitacao = self.request.GET.get("id")
        situacao = self.request.GET.get("situacao")
        folha_ponto = SendingTimeSheet.objects.get(pk=id_solicitacao)
        query = self.queryset.filter(
            Q(
                Q(portalrequestusufruct__isnull=False)
                & Q(
                    portalrequestusufruct__activity__usufructs__start_date__year=folha_ponto.reference_year,
                    portalrequestusufruct__activity__usufructs__start_date__month=folha_ponto.reference_month,
                )
                | Q(
                    portalrequestusufruct__activity__usufructs__end_date__year=folha_ponto.reference_year,
                    portalrequestusufruct__activity__usufructs__end_date__month=folha_ponto.reference_month,
                )
            )
            | Q(
                Q(portalrequestabsence__isnull=False)
                & Q(
                    Q(
                        portalrequestabsence__start_date__year=folha_ponto.reference_year,
                        portalrequestabsence__start_date__month=folha_ponto.reference_month,
                    )
                    | Q(
                        portalrequestabsence__end_date__year=folha_ponto.reference_year,
                        portalrequestabsence__end_date__month=folha_ponto.reference_month,
                    ),
                )
            ),
            Q(employee=folha_ponto.employee),
        ).exclude(status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT])
        if situacao:
            query = query.filter(status=situacao)
        return self.filter_queryset(query)

    def list(self, request):
        id_solicitacao = request.GET.get("id")
        if id_solicitacao is None:
            return Response(
                {"erro": "A requisição deve enviar o parâmetro id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)
