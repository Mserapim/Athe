from rh.pvf.apiv2.utils.retification import usufrutos_retificados_ids
from rh.pvf.models import (
    PVFIndividualVacation,
    PVFElectoralSlack,
    PVFRegularVacation,
    PVFForensicRecess,
    PVFServerShift,
    PVFIntershipCompetition,
    PVFCompClearanceMembers,
    PVFCompVactionMembers,
    PVFSolicitacaoEstagiario,
    PVFSolicitacaoResidente,
    PVFSubstitutePromoterContest,
    PVFBloodDonation,
)
from rh.pvf.apiv2.serializers.usufructserializers import *
from rh.models import Servidor
from rh.pvf.const import *
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rh.pvf.apiv2.filters import PVFAcquisitionPeriodFilter, PVFVactionConfigFilter
from rest_framework.views import APIView
from contrib.middleware import set_current_user
from django.shortcuts import get_object_or_404
from apiv2.utils import response_api_view
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rh.dayoff.models import AcquisitionPeriod, Usufruct
from rest_framework.decorators import action
from django.db.models import Q

from rh.pvf.utils.utils import get_period_aquisitivos_ordernados


class PVFAcquisitionPeriodViewSet(BaseRequestViewSet):
    """
    View dos períodos aquisitivo dos servidor logado
    """

    queryset = AcquisitionPeriod.objects.all()
    serializer_class = PVFAcquisitionPeriodSerializer
    filterset_class = PVFAcquisitionPeriodFilter

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee, days_not_booked_cache__gt=0)
        return self.filter_queryset(queryset)

    def list(self, request):
        sorted_queryset = get_period_aquisitivos_ordernados(self.get_queryset())
        serializer = PVFAcquisitionPeriodSerializer(sorted_queryset, many=True)
        return response_api_view(serializer.data)


class PVFUsufrctViewSet(BaseRequestViewSet):
    """
    View das programações de usufrutos marcadas
    """

    queryset = Usufruct.objects.all()
    serializer_class = PVFUsufructSerializer

    @action(detail=True, methods=["GET"])
    def request_usufructs(self, request, pk=None):
        queryset = self.queryset.filter(
            Q(activity__activity_requests__id=pk) | Q(cancel_usufruct__id=pk)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)

    def get_queryset(self):
        return self.filter_queryset(self.queryset)


class PVFUsufrutoRetificadoView(BaseRequestViewSet):
    """
    View das programações de usufrutos a serem retificados
    """

    queryset = Usufruct.objects.all()
    serializer_class = PVFUsufructSerializer

    @action(detail=True, methods=["GET"])
    def usufrutos_retificados(self, request, pk=None):
        consulta = self.queryset.filter(pk__in=usufrutos_retificados_ids(pk))
        pagina = self.paginate_queryset(consulta)
        if pagina is not None:
            serializador = self.get_serializer(pagina, many=True)
            return self.get_paginated_response(serializador.data)
        serializador = self.get_serializer(consulta, many=True)
        return response_api_view(serializador.data)

    def get_queryset(self):
        return self.filter_queryset(self.queryset)


class PVFAlterarPagamentoUsufrutoViewSet(GenericViewSet):
    """
    View da envio da alteração de pagamento
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = Usufruct.objects.filter()
    serializer_class = PVFUsufructSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="usufruct_pk", description="Id do usufruto", type=int
            ),
            OpenApiParameter(
                name="competence", description="Competência: MM/AAAA", type=str
            ),
            OpenApiParameter(
                name="qtd_parcel", description="Quantidade de parcelas", type=int
            ),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "usufruct_pk": {"type": "integer"},
                    "competence": {"type": "string"},
                    "qtd_parcel": {"type": "integer"},
                },
            },
        },
    )
    @action(detail=False, methods=["POST"])
    def payment(self, request, pk=None):
        set_current_user(request.user)
        params = request.data
        serializer_data = self.serializer_class().payment(params)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFVactionConfigView(APIView):
    """
    Lista de combinações de férias
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="type_usufruct", description="usufruto", type=int),
            OpenApiParameter(name="total_days", description="Toral de dias", type=int),
            OpenApiParameter(name="rectification", description="Retificação", type=int),
        ]
    )
    def get(self, request):
        """Retorna a lista de combinações de férias"""
        employee = Servidor.objects.get(user=self.request.user)
        type_usufruct = request.GET.get("type_usufruct", None)
        total_days = request.GET.get("total_days", None)
        config = PVFVactionConfigFilter.filter_config_vacation(
            type_usufruct, total_days, employee
        )
        serializer_data = PVFVacationConfigSerializer(config, many=True).data
        return response_api_view(serializer_data)


class PVFPreValidacaoUsufrutoView(APIView):
    """
    View da pré validação dos usufrutos
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRequestUsufruct.objects.filter()
    serializer_class = PVFPreValidacaoUsufrutoSerializador

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "type_usufruct": {"type": "integer"},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        dados = request.data
        dados_serializados = self.serializer_class().pre_validacao(dados)
        if dados_serializados["success"]:
            return Response(dados_serializados, status=status.HTTP_200_OK)
        return Response(dados_serializados, status=status.HTTP_400_BAD_REQUEST)


class PVFRequestUsufructViewSet(GenericViewSet):
    """
    View das solicitações de usufrutos VDF
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = None
    serializer_class = None
    portal_request_type = None

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(
            employee=employee, portal_request_type=self.portal_request_type
        )
        return queryset

    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação"""
        return self.create(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "usufructs_in": {
                        "type": "[{start_date:date,end_date:date,days:0,sale_usufruct:0,parcel_number:0}]"
                    },
                    "type_usufruct": {"type": "integer"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
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


class PVFRegularVacationViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de férias regulamentares VDF
    """

    queryset = PVFRegularVacation.objects.filter()
    serializer_class = PVFRegularVacationSerializer
    portal_request_type = PORTAL_REGULAR_VACATION_TYPE


class PVFIndividualVacationViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de férias individuais VDF
    """

    queryset = PVFIndividualVacation.objects.filter()
    serializer_class = PVFIndividualVacationSerializer
    portal_request_type = PORTAL_INDIVIDUAL_VACATION_TYPE


class PVFElectoralSlackViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de dispensa eleitoral VDF
    """

    queryset = PVFElectoralSlack.objects.filter()
    serializer_class = PVFElectoralSlackSerializer
    portal_request_type = PORTAL_ELECTORAL_SLACK_TYPE


class PVFForensicRecessViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de recesso forense VDF
    """

    queryset = PVFForensicRecess.objects.filter()
    serializer_class = PVFForensicRecessSerializer
    portal_request_type = PORTAL_FORENSIC_RECESS_TYPE


class PVFServerShiftViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de plantão servidores VDF
    """

    queryset = PVFServerShift.objects.filter()
    serializer_class = PVFServerShiftSerializer
    portal_request_type = PORTAL_SERVER_SHIFT_TYPE


class PVFIntershipCompetitionViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de concurso de estagiários VDF
    """

    queryset = PVFIntershipCompetition.objects.filter()
    serializer_class = PVFIntershipCompetitionSerializer
    portal_request_type = PORTAL_INTERNSHIP_COMPETITION_TYPE


class PVFCompClearanceMembersViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de folgas compensatórias de membros VDF
    """

    queryset = PVFCompClearanceMembers.objects.filter()
    serializer_class = PVFCompClearanceMembersSerializer
    portal_request_type = PORTAL_COMP_CLEARANCE_MEMBERS_TYPE


class PVFCompVactionMembersViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações plantão de recesso forense de membros VDF
    """

    queryset = PVFCompVactionMembers.objects.filter()
    serializer_class = PVFCompVactionMembersSerializer
    portal_request_type = PORTAL_COMP_VACATION_MEMBERS_TYPE


class PVFSubstitutePromoterContestViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de concurso de promotor substituto VDF
    """

    queryset = PVFSubstitutePromoterContest.objects.filter()
    serializer_class = PVFSubstitutePromoterContestSerializer
    portal_request_type = PORTAL_SUBSTITUTE_PROMOTER_CONTEST_TYPE


class PVFBloodDonationViewSet(PVFRequestUsufructViewSet):
    """
    View das solicitações de doação de sangue VDF
    """

    queryset = PVFBloodDonation.objects.filter()
    serializer_class = PVFBloodDonationtSerializer
    portal_request_type = PORTAL_BLOOD_DONATION_TYPE


class PVFSolicitacaoEstagiarioView(PVFRequestUsufructViewSet):
    """
    View das solicitações de recesso de estagiário VDF
    """

    queryset = PVFSolicitacaoEstagiario.objects.filter()
    serializer_class = PVFSolicitacaoEstagiarioSerializer
    portal_request_type = PORTAL_INTERNS_RECESS_TYPE


class PVFSolicitacaoResidenteView(PVFRequestUsufructViewSet):
    """
    View das solicitações de recesso de residente VDF
    """

    queryset = PVFSolicitacaoResidente.objects.filter()
    serializer_class = PVFSolicitacaoResidenteSerializer
    portal_request_type = PORTAL_RESIDENTS_RECESS_TYPE
