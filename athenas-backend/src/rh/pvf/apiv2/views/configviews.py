import calendar
from datetime import date
from apiv2.baseviews import ListBaseView
from apiv2.utils import response_api_view
from auth.permissions.vdf.permissions import IsPermissionVDF
from rh.afastamento.models import CID
from rh.gfp.models import ContraCheque, FolhaTipo
from rh.pvf.apiv2.serializers.baseserializers import *
from rh.models import (
    ConfigPeriodoCumulativoSubstituicao,
    Lotacao,
    MovimentacaoTeletrabalho,
    Servidor,
)
from rh.pvf.apiv2.serializers.configserializers import (
    PVFConfigValueSerializer,
    PVFListCIDSerializer,
    PVFListMonthYearSerializer,
    PVFListaAnoFichaFinaceiraSerializador,
    PVFTypesPayrollSerializer,
)
from rh.pvf.apiv2.utils.base import get_permissions
from rh.pvf.apiv2.utils.report import (
    get_months,
    get_teams,
    get_year_calendar,
    get_years_paycheck,
    get_years_point_sheet,
    lista_ano_ficha_financeira,
)
from rh.pvf.apiv2.utils.telework import (
    aprovador_semestral,
    telework_pending,
    tp_solicitacao_teletrabalho,
)
from rh.pvf.apiv2.views.baseviews import BaseRequestViewSet
from standard.models import Choice
from standard.models import Item
from rest_framework.permissions import IsAuthenticated
from rh.pvf.apiv2.utils.approval import (
    get_employee_approver,
    group_list,
    belongs_group_dgp,
    group_list_all,
)
from drf_spectacular.utils import OpenApiParameter, extend_schema
from django.db.models import Q
from rest_framework.response import Response
from rh.pvf.const import *
from contrib.base_converter import str_to_bool


class PVFConfigTypeViewSet(BaseRequestViewSet):
    """
    View da configuração tipo de solicitação
    """

    queryset = Choice.objects.filter(name="REQUEST_TYPE_VDF").order_by("label")
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)


class PVFConfigStatusViewSet(BaseRequestViewSet):
    """
    View da configuração do status da solicitação
    """

    queryset = Choice.objects.filter(name="REQUEST_STATUS").order_by("label")
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)


class PVFConfigStepViewSet(BaseRequestViewSet):
    """
    View da configuração da Etapa/Aprovador da solicitação
    """

    queryset = Choice.objects.filter(active=True)
    serializer_class = PVFConfigStepSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        return self.queryset.filter(name="REQUEST_STEP").exclude(value=8)


class PVFConfigTypeEmployeeView(ListBaseView):
    """
    View da configuração tipo de servidor
    """

    queryset = Choice.objects.filter(active=True)
    serializer_class = PVFConfigTypeEmployeeSerializer
    full_text_index = ("label__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista configuração tipo de servidor
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        dados_paginacao = self.paginate_queryset(TYPE_EMPLOYEE)
        keyword = self.request.query_params.get(
            "keyword"
        ) or self.request.query_params.get("palavra_chave")

        if dados_paginacao is not None:
            if keyword:
                dados_paginacao = [
                    item
                    for item in dados_paginacao
                    if keyword.lower() in item["label"].lower()
                ]
            dados_serializados = self.serializer_class(dados_paginacao, many=True).data
            return self.get_paginated_response(dados_serializados)
        dados_serializados = self.serializer_class(dados_paginacao, many=True).data
        return response_api_view(dados_serializados)


class PVFConfigMarkSituationViewSet(BaseRequestViewSet):
    """
    View da configuração da situação da meta
    """

    queryset = Choice.objects.filter(active=True)
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        return self.queryset.filter(name="MARK_SITUATION")


class PVFConfigTypeShiftViewSet(BaseRequestViewSet):
    """
    View da configuração das permissões de plantões em que o servidor pode informar escala
    """

    queryset = Choice.objects.filter(active=True)
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        if self.request.query_params.get("todos_tipos", None):
            valores_especificos = [
                TYPE_SHIFT_DTI,
                TYPE_SHIFT_WEEKEND,
                TYPE_SHIFT_RECESS,
                TYPE_SHIFT_ELECTORAL,
                TIPO_PLANTAO_PGJ,
            ]
            return self.queryset.filter(
                name="TYPE_SHIFT", value__in=valores_especificos
            )

        employee = Servidor.objects.get(user=self.request.user)
        permissions = get_permissions(employee)
        return self.queryset.filter(name="TYPE_SHIFT", value__in=permissions)


class PVFTypeShiftViewSet(BaseRequestViewSet):
    """
    View dos tipos de plantões em que o servidor pode informar escala
    """

    queryset = Choice.objects.filter(active=True)
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        return self.queryset.filter(name="TYPE_SHIFT").exclude(
            value__in=[6, 7, 8, 9, 10]
        )


class PVFSubstituteCandidateViewSet(BaseRequestViewSet):
    """
    View da lista de candidato à substitutos
    """

    queryset = Servidor.objects.filter(ativo=True)
    serializer_class = PVFSubstituteCandidateSerializer
    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "matricula__iexact",
    )

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        type_server = employee.tipo
        queryset = self.queryset.filter(tipo=type_server)
        return self.filter_queryset(queryset)


class PVFTypeAbsenceViewSet(BaseRequestViewSet):
    """
    View dos tipos de afastamento por tipo(type_by_possession) e sexo do usuário
    """

    queryset = Choice.objects.filter()
    serializer_class = PVFTypeAbsenceSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        keys = []
        if employee.type_by_possession in ["EST", "RES"]:
            keys.append("afastamentos_estagiarios")
        else:
            if employee.type_by_possession in ["MBR", "MEL", "MEC"]:
                keys.append("afastamento_membros")
            else:
                keys.append("afastamentos_servidores")

            if employee.pessoa_fisica.sexo == "M":
                keys.append("afastameto_masculino")
            else:
                keys.append("afastamento_feminino")

        configs = Item.objects.filter(key__in=keys)
        values = []
        for config in configs:
            if config.value:
                values = values + config.value.split(",")
        return self.queryset.filter(name="ABSENCE_TYPE_VDF", value__in=values)


class PVFTipoSolicitacaoView(BaseRequestViewSet):
    """
    View da lista dos tipos de solicitações por usuário
    """

    queryset = Choice.objects.filter()
    serializer_class = PVFTipoSolicitacaoSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        key = None
        if employee.type_by_possession == "EST":
            key = "solicitacoes_estagiarios"
        elif employee.type_by_possession == "RES":
            key = "solicitacao_residentes"
        elif employee.type_by_possession in ["MBR", "MEL", "MEC"]:
            key = "solicitacoes_membros"
        elif employee.type_by_possession == "CMS":
            key = "solicitacoes_comissionados"
        elif employee.type_by_possession in ["EFE", "ECM", "EFC"]:
            key = "solicitacoes_efetivos"
        else:
            key = "solicitacoes_servidores"

        config = Item.objects.filter(key=key).first()
        values = []
        if config and config.value:
            values = config.value.split(",")

        if telework_pending(employee) and not employee.ultimo_teletrabalho_revogado:
            values.append(tp_solicitacao_teletrabalho(employee))

        data_atual = datetime.today().date()
        if ConfigPeriodoCumulativoSubstituicao.objects.filter(
            data_inicio_periodo__lte=data_atual, data_fim_periodo__gte=data_atual
        ).exists() and employee.type_by_possession in ["MBR", "MEL", "MEC"]:
            values.append(PORTAL_CUMULATIVE_EXERCISE_TYPE)

        if aprovador_semestral(employee, data_atual):
            values.append(PORTAL_RELATORIO_TELETRABALHO_SEMESTRAL_TYPE)

        return self.queryset.filter(name="REQUEST_TYPE_VDF", value__in=values)


class PVFApprovalsEmployeeViewSet(BaseRequestViewSet):
    """
    View da lista de servidores ativos para o filtro de aprovações
    """

    queryset = Servidor.objects.filter(ativo=True)
    serializer_class = PVFEmployeeSerializer
    full_text_index = ("pessoa_fisica__nome__icontains",)

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset
        if not belongs_group_dgp(employee):
            queryset = queryset.filter(
                Q(portal_request_employee__approver__pk=employee.pk)
                | Q(portal_request_employee__step_current__in=group_list(employee))
                | Q(
                    portal_request_employee__portalrequesthistory__group__in=list(
                        get_employee_approver(employee)
                    )
                )
                | Q(
                    portal_request_employee__portalrequesthistory__user=self.request.user
                )
                & Q(
                    portal_request_employee__portalrequesthistory__action__in=[
                        REQUEST_ACT_DEFER,
                        REQUEST_ACT_INDEFER,
                        REQUEST_ACT_SCIENCE,
                        REQUEST_ACT_ANNOTATION,
                        REQUEST_ACT_EFFECTIVENESS,
                    ]
                )
            ).distinct()
        else:
            groups = group_list_all()
            queryset = queryset.filter(
                portal_request_employee__step_current__in=groups
            ).distinct()
        return self.filter_queryset(queryset)


class PVFEmployeeViewSet(BaseRequestViewSet):
    """
    View da lista de servidores
    """

    queryset = Servidor.objects.filter(ativo=True)
    serializer_class = PVFEmployeeSerializer
    full_text_index = (
        "pessoa_fisica__nome__unaccent__icontains",
        "matricula__icontains",
    )

    def get_queryset(self):
        return self.filter_queryset(self.queryset)


class PVFWorkplaceViewSet(BaseRequestViewSet):
    """
    View da lista de lotações
    """

    queryset = Lotacao.objects.filter(ativo=True)
    serializer_class = PVFWorkplaceDutySerializer
    full_text_index = ("nome__icontains",)

    def get_queryset(self):
        return self.filter_queryset(self.queryset)


class PVFListYearPointSheetView(ListBaseView):
    """
    View da lista de anos do folha ponto
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista de anos do folha ponto
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_years_point_sheet()
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFListYearCalendarView(ListBaseView):
    """
    View da lista de anos do calendário
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista de anos de anos do calendário
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_year_calendar()
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFListCalendarTeamsView(ListBaseView):
    """
    View da lista de equipes do responsável
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista da equipes do responsável
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        employee = Servidor.objects.get(user=request.user)
        data = get_teams(employee)
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = PVFConfigValueSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = PVFConfigValueSerializer(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFListTypeCalendarView(ListBaseView):
    """
    View da lista do tipo calendário (completo ou reduzido)
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista do tipo calendário (completo ou reduzido)
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = [
            {"id": 1, "description": "Completo"},
            {"id": 2, "description": "Reduzido"},
        ]
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = PVFConfigValueSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = PVFConfigValueSerializer(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFListYearPayCheckView(ListBaseView):
    """
    View da lista de anos do contracheque
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista de anos do contracheque
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_years_paycheck()
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFListMonthView(ListBaseView):
    """
    View da lista de meses
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista de meses
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_months()
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = PVFListMonthYearSerializer(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFTypesPayrollViewSet(BaseRequestViewSet):
    """
    View dos tipos de folha
    """

    queryset = FolhaTipo.objects.filter(ativo=True)
    serializer_class = PVFTypesPayrollSerializer

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")
        paychecks = ContraCheque.objects.filter(
            servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf,
            folha__available_pvf=True,
            folha__periodo__mes=month,
            folha__periodo__ano=year,
        )
        queryset = self.queryset.filter(folhas__paychecks__in=paychecks).distinct()
        return self.filter_queryset(queryset)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="month", description="Mês", type=int),
            OpenApiParameter(name="year", description="Ano", type=int),
        ]
    )
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFConfigGroupEventView(BaseRequestViewSet):
    """
    View da lista de grupo de eventos de calendário
    """

    queryset = Choice.objects.all()
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        return self.queryset.filter(name="GROUP_EVENT_NAME")


class PVFConfigCIDView(BaseRequestViewSet):
    """
    View da lista de cids (classificação internacional de doenças)
    """

    queryset = CID.objects.all()
    serializer_class = PVFListCIDSerializer
    full_text_index = ("description__icontains", "cid_code__code__icontains")

    def get_queryset(self):
        return self.filter_queryset(self.queryset)


class PVFListaAnoFichaFinanceiraView(ListBaseView):
    """
    View da lista de anos da ficha financeira
    """

    queryset = Choice.objects.all()
    serializer_class = PVFListaAnoFichaFinaceiraSerializador
    permission_classes = [IsAuthenticated, IsPermissionVDF]
    full_text_index = ("label__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista de anos ficha financeira
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        dados = lista_ano_ficha_financeira()
        dados_paginacao = self.paginate_queryset(dados)
        if dados_paginacao is not None:
            dados_serializados = self.serializer_class(dados_paginacao, many=True).data
            return self.get_paginated_response(dados_serializados)
        dados_serializados = self.serializer_class(dados_paginacao, many=True).data
        return response_api_view(dados_serializados)


class PVFConfigTipoFolga(ListBaseView):
    """
    View da configuração tipos de folgas
    """

    queryset = Choice.objects.all()
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)

    def get_queryset(self):
        return self.queryset.filter(name="TIPO_FOLGA").order_by("label")


class PVFHistoricoConfigAcaoView(ListBaseView):

    queryset = Choice.objects.filter(name="ACTION_TAKEN").order_by("label")
    serializer_class = PVFConfigTypeSerializer
    full_text_index = ("label__icontains",)


class PVFServidoresView(ListBaseView):
    """
    View da lista de servidores
    """

    full_text_index = (
        "pessoa_fisica__nome__unaccent__icontains",
        "matricula__icontains",
    )
    serializer_class = PVFServidorSerializer

    def get_queryset(self):
        situacao = self.request.query_params.get("situacao", None)
        situacao_bool = str_to_bool(situacao) if isinstance(situacao, str) else None
        if situacao_bool is not None:
            return Servidor.objects.filter(ativo=situacao_bool)
        return Servidor.objects.all()
