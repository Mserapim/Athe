from collections import defaultdict
from django.shortcuts import get_object_or_404
from apiv2.baseviews import ApiCore, ListBaseView
from apiv2.utils import response_api_view
from rh.const import STATUS_TELETRABALHO_BLOQUEADO
from rh.models import MovimentacaoTeletrabalho, Servidor
from rh.pvf.apiv2.utils.telework import (
    qtd_plano_trabalho,
    is_workplan,
    telework_pending,
    telework_pending_id,
)
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rh.pvf.const import MSG_DEFAULT_ATO_TELETRABALHO, STS_EFFECTIVE
from rh.pvf.models import MarkTelework, RelatorioSemestralTeletrabalho, SendingTelework
from rh.pvf.apiv2.serializers.sendteleworkserializers import (
    PVFConfigTeleworkEmployeeSerializer,
    PVFDesbloqueioTeletrabalhoSerializer,
    PVFListaRelatorioSemestralTeletrabalhoSerializer,
    PVFMarkTeleworkSerializer,
    PVFRelatorioSemestralTeletrabalhoSerializer,
    PVFSendTeleworkSerializer,
    PVFSolicitacaoTeletrabalhoAfastamentosSerializer,
)
from rh.dayoff.const import *
from contrib.middleware import set_current_user
from rest_framework import status
from rest_framework.decorators import action
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rh.pvf.utils.teletrabalho import get_teletrabalhos_semestrais
from datetime import datetime
from dateutil.relativedelta import relativedelta
from rh.afastamento.models import BaseLicencaAfastamento
from django.db.models.query_utils import Q
from rest_framework.views import APIView
import calendar


from contrib.utils import DateUtils, getLogger

log = getLogger(__name__)


class PVFMarkTeleworkViewSet(GenericViewSet):
    """
    View da criação das meta do teletrabalho
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = MarkTelework.objects.filter()
    serializer_class = PVFMarkTeleworkSerializer

    def get_queryset(self):
        return self.queryset.filter()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        response = serializer.perform_update(instance)
        return Response(response, status=response["code"])

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class PVFCreateTeleworkViewSet(GenericViewSet):
    """
    View da criação da solicitação de teletrabalho
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = SendingTelework.objects.filter()
    serializer_class = PVFSendTeleworkSerializer

    def get_queryset(self):
        return self.queryset.filter()

    def post(self, request, *args, **kwargs):
        """Cria um novo envio do teletrabalho"""
        return self.create(request, *args, **kwargs)

    def create(self, request):
        set_current_user(request.user)
        # data = request.data
        serializer_data = self.serializer_class().create()
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFSendTeleworkViewSet(GenericViewSet):
    """
    View da envio da solicitação de teletrabalho
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = SendingTelework.objects.filter()
    serializer_class = PVFSendTeleworkSerializer

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "targets": {
                        "type": "[{id:integer,total_completed:integer,mark_situation:integer,anexo_id:integer}]"
                    },
                    "observation": {"type": "string"},
                    "anexo_id": {"type": "integer"},
                },
            },
        },
    )
    @action(detail=False, methods=["POST"])
    def send(self, request, pk=None):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().send(data, pk)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFListMarkTeleworkView(BaseRequestViewSet):
    """
    View da lista metas da solicitação do teletrabalho
    """

    queryset = MarkTelework.objects.filter()
    serializer_class = PVFMarkTeleworkSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    @action(detail=True, methods=["GET"])
    def request_targets(self, request, pk=None):
        queryset = self.queryset.filter(request__pk=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFListaTeletrabalhoView(ListBaseView):
    """
    View da lista de teletrabalhos do planto atual
    """

    queryset = SendingTelework.objects.filter()
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFSendTeleworkSerializer

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
            servidor=employee
        ).order_by("-id")[:3]
        querset = self.queryset.filter(
            employee=employee,
            work_plan__in=mov_teletrabalho,
            status=STS_EFFECTIVE,
            cancelado_solicitacao=False,
        )
        return querset.order_by("-id")

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista de teletrabalhos do planto atual
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


class PVFConfigTeleworkEmployeeView(ListBaseView):
    """
    View que retorna as informações de teletrabalho do servidor
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFConfigTeleworkEmployeeSerializer

    def get(self, request, *args, **kwargs):
        """
        Informações do teletrabalho do servidor
        """
        employee = Servidor.objects.get(user=self.request.user)
        set_current_user(request.user)
        data = {}
        data.update(
            {
                "active_workplan": is_workplan(employee),
                "telework_pending": telework_pending(employee),
                "telework_id": telework_pending_id(employee),
                "send_workplan_reference": qtd_plano_trabalho(),
            }
        )
        # data_serializer = self.serializer_class(data,many=True).data
        return Response(data)


class PVFListaRelatorioSemestralTeletrabalhoView(ListBaseView):
    """
    View que retorna as informações de teletrabalho por aprovador de acordo com o perido definido
    em ConfigPeriodoEnvioRelatoriosSemestrais
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFListaRelatorioSemestralTeletrabalhoSerializer

    def get(self, request, *args, **kwargs):
        """
        Lista de teletrabalhos aprovados pelo current_user
        """

        employee = Servidor.objects.get(user=self.request.user)
        set_current_user(request.user)
        teletrabalhos = get_teletrabalhos_semestrais(employee)
        if teletrabalhos:
            # Agrupar por tipo de ato, matrícula e nome
            grouped_data = defaultdict(list)
            for teletrabalho in teletrabalhos.order_by("servidor__matricula"):
                key = (
                    teletrabalho.get_tipo_ato_display(),
                    teletrabalho.servidor.matricula,
                    teletrabalho.servidor.pessoa_fisica.social_name,
                )
                detalhes = PVFListaRelatorioSemestralTeletrabalhoSerializer(
                    teletrabalho
                ).get_detalhes_teletrabalho(teletrabalho)
                grouped_data[key].append(detalhes)

            # Agrupar por tipo de ato
            grouped_by_tipo_ato = defaultdict(list)
            for (tipo_ato, matricula, nome), registros in grouped_data.items():
                grouped_by_tipo_ato[tipo_ato].append(
                    {"matricula": matricula, "nome": nome, "registros": registros}
                )

            grouped_data_response = [
                {"tipo_ato": tipo_ato, "dados": dados}
                for tipo_ato, dados in grouped_by_tipo_ato.items()
            ]
            return response_api_view(grouped_data_response)
        else:
            return response_api_view([])


class PVFRelatorioSemestralTeletrabalhoView(GenericViewSet):
    """
    View da envio da solicitação semestral do teletrabalho
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = RelatorioSemestralTeletrabalho.objects.all()
    serializer_class = PVFRelatorioSemestralTeletrabalhoSerializer

    def post(self, request, *args, **kwargs):
        """Cria um novo envio do teletrabalho"""
        return self.create(request, *args, **kwargs)

    def create(self, request):
        set_current_user(request.user)
        dados = request.data
        serializer_data = self.serializer_class().create(dados)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)


class PVFSolicitacaoTeletrabalhoAfastamentos(ListBaseView):
    """
    View dos afastamentos abertos durante a competência da solicitação do teletrabalho
    """

    queryset = BaseLicencaAfastamento.objects.filter()
    serializer_class = PVFSolicitacaoTeletrabalhoAfastamentosSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="mes", description="Mês de referência do teletrabalho", type=int
            ),
            OpenApiParameter(
                name="ano", description="Ano de referência do teletrabalho", type=int
            ),
            OpenApiParameter(
                name="servidor_id", description="Id do servidor", type=int
            ),
            OpenApiParameter(
                name="solicitacao_id", description="Id da solicitação", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista dos afastamentos na referêcia do teletrabalho
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        mes = int(self.request.GET.get("mes"))
        ano = int(self.request.GET.get("ano"))
        servidor_id = self.request.GET.get("servidor_id")
        solicitacao_id = self.request.GET.get("solicitacao_id")

        ultimo_dia = calendar.monthrange(ano, mes)[1]
        data_inicio = datetime(ano, mes, 1).date()
        data_fim = datetime(ano, mes, ultimo_dia).date()

        query = (
            BaseLicencaAfastamento.objects.filter(
                servidor__pk=servidor_id,
            )
            .filter(
                Q(data_inicio__gte=data_inicio, data_inicio__lte=data_fim)
                | Q(
                    Q(data_inicio__lte=data_inicio) & Q(data_fim__gte=data_inicio)
                    | Q(data_fim__isnull=True)
                )
            )
            .exclude(estado__in=[4])  # CANCELADO
        )
        if solicitacao_id:
            solicitacao = SendingTelework.objects.get(pk=solicitacao_id)
            query = query.exclude(created_at__gt=solicitacao.date)

        return self.filter_queryset(query)

    def list(self, request):
        mes = request.GET.get("mes")
        ano = request.GET.get("ano")
        servidor_id = request.GET.get("servidor_id")
        if mes is None:
            return Response(
                {"erro": "A requisição deve enviar o parâmetro mes"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ano is None:
            return Response(
                {"erro": "A requisição deve enviar o parâmetro ano"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if servidor_id is None:
            return Response(
                {"erro": "A requisição deve enviar o parâmetro servidor_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFInfoTeleBloqueado(APIView):

    def get(self, request, *args, **kwargs):
        """
        View da infos do tele bloqueado
        """
        set_current_user(request.user)
        mov_teles = MovimentacaoTeletrabalho.objects.filter(
            servidor=request.user.servidor, situacao=STATUS_TELETRABALHO_BLOQUEADO
        )
        data = []
        mes, ano = SendingTelework.get_reference_year_month()
        for mov_tele in mov_teles:
            ultimo_historico = mov_tele.historico_movteletrabalho.last()
            msg = (
                ultimo_historico.observacao
                if ultimo_historico and ultimo_historico.observacao
                else MSG_DEFAULT_ATO_TELETRABALHO
            )
            data.append(
                {
                    "referencia": f"{mes}/{ano}",
                    "vigencia": f"{DateUtils.date_to_str(mov_tele.data_inicio)} até {DateUtils.date_to_str(mov_tele.data_fim)}",
                    "motivo": msg,
                }
            )
        return response_api_view(data)


class PVFDesbloqueioTeletrabalhoView(ApiCore):
    """
    View da criação da solicitação de desbloqueio do teletrabalho
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PVFDesbloqueioTeletrabalhoSerializer

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "anexo_id": {"type": "integer"},
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
