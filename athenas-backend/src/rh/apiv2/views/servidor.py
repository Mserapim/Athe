from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from contrib.middleware import set_current_user
from auth.backend import MultiAuthentication
from apiv2.baseviews import ListBaseView, BaseViewSet, ApiDetailView
from rh.apiv2.serializers.servidor import (
    SMCMembrosSerializer,
    AtualizaEmailPessoalSerializador,
    UsufrutoFeriasSerializer,
    ValidaEmailPessoalSerializador,
    ServidorListagemSerializer,
    TipoPosseSerializer,
)
from rh.dayoff.const import (
    INDIVIDUAL_VACATION,
    REGULAR_VACATIONS,
    USU_AUTORIZED_CI,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_NEW,
    USU_SUBSTITUTE,
)
from rh.dayoff.models import Usufruct
from rh.models import PessoaFisica, Servidor
from standard.models import Choice
from contrib.utils import getLogger
from django.db.models import Q


log = getLogger(__name__)


class SMCMembrosview(ListBaseView):
    """
    View da lista de membros para o sistema SMC
    """

    permission_classes = [IsAuthenticated]
    queryset = PessoaFisica.objects.filter()
    authentication_classes = [MultiAuthentication]
    serializer_class = SMCMembrosSerializer
    full_text_index = ("nome__unaccent__icontains",)

    def get_queryset(self):
        queryset = self.queryset.filter(
            servidor__ativo=True, servidor__type_by_possession__in=["MBR", "MEL"]
        )
        return self.filter_queryset(queryset)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do lista de membros ativos
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AtualizaEmailPessoalViewSet(BaseViewSet):
    """
    View da atualização de e-mail pessoal
    """

    permission_classes = [
        IsAuthenticated,
    ]
    queryset = PessoaFisica.objects.filter()
    serializer_class = AtualizaEmailPessoalSerializador

    def post(self, request, *args, **kwargs):
        """Atualiza email pessoal"""
        return self.create(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email_pessoal": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        dados = request.data
        dados_serializados = self.serializer_class().registrar_email_pessoal(dados)
        if dados_serializados["success"]:
            return Response(dados_serializados, status=status.HTTP_200_OK)
        return Response(dados_serializados, status=status.HTTP_400_BAD_REQUEST)


class ValidaEmailPessoalViewSet(BaseViewSet):
    """
    View da validação de e-mail pessoal
    """

    permission_classes = [
        IsAuthenticated,
    ]
    queryset = PessoaFisica.objects.filter()
    serializer_class = ValidaEmailPessoalSerializador

    def post(self, request, *args, **kwargs):
        """Valida email pessoal"""
        return self.create(request, *args, **kwargs)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "codigo_email": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        dados = request.data
        dados_serializados = self.serializer_class().validar_email_pessoal(dados)
        if dados_serializados["success"]:
            return Response(dados_serializados, status=status.HTTP_200_OK)
        return Response(dados_serializados, status=status.HTTP_400_BAD_REQUEST)


class ServidorListagemView(ListBaseView):
    """
    View da lista da lista de Serivores


    Parametros esperados:
        keyword : busca por nome , cpf e matricula;
        tipo_dados_pessoais : basico ou completo, se não for enviado será considerado basico como padrão;
        tipo_dados_servidor : basico ou completo, se não for enviado será considerado basico como padrão;
        situacao: Vazio, False ou True;
        tipo_posse : lista de tipos posse fornecido pela api tipo_posses;

    """

    permission_classes = [IsAuthenticated]
    queryset = Servidor.objects.filter()
    authentication_classes = [MultiAuthentication]
    serializer_class = ServidorListagemSerializer
    full_text_index = (
        "matricula__iexact",
        "pessoa_fisica__nome__unaccent__icontains",
        "pessoa_fisica__social_name__unaccent__icontains",
        "pessoa_fisica__cpf__iexact",
        "user__username__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="tipo_dados_pessoais",
                description="Tipo dados Pessoais - baisco/completo",
                type=str,
            ),
            OpenApiParameter(
                name="tipo_dados_servidor",
                description="Tipo dados Servidor - baisco/completo",
                type=str,
            ),
            OpenApiParameter(name="situacao", description="Situação", type=bool),
            OpenApiParameter(name="tipo_posse", description="Tipo Posse", type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        tipo_posse = self.request.GET.getlist("tipo_posse", None)
        if tipo_posse is None or tipo_posse == []:
            tipo_posse = self.request.GET.getlist("tipo_posse[]", None)

        if tipo_posse:
            queryset = queryset.filter(type_by_possession__in=tipo_posse)

        tipo_posse_exclude = self.request.GET.getlist("tipo_posse_exclude", None)
        if tipo_posse_exclude is None or tipo_posse_exclude == []:
            tipo_posse_exclude = self.request.GET.getlist("tipo_posse_exclude[]", None)

        if tipo_posse_exclude:
            queryset = queryset.exclude(type_by_possession__in=tipo_posse_exclude)

        situacao = self.request.GET.get("situacao", None)
        if situacao is not None:
            situacao = True if situacao.lower() == "true" else False
            queryset = queryset.filter(ativo=situacao)

        return queryset


class ServidorDetailView(ApiDetailView):
    model = Servidor
    authentication_classes = [MultiAuthentication]
    serializer_class = ServidorListagemSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id", description="Chave primario(Primary Key)", type=int
            ),
            OpenApiParameter(
                name="tipo_dados_pessoais",
                description="Tipo dados Pessoais - baisco/completo",
                type=str,
            ),
            OpenApiParameter(
                name="tipo_dados_servidor",
                description="Tipo dados Servidor - baisco/completo",
                type=str,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TipoPosseView(ListBaseView):
    """
    View da lista da lista de Tipos de Posse
    """

    permission_classes = [IsAuthenticated]
    queryset = Choice.objects.filter(name="CLASSIF_EMPLOYEE_BY_POSSESSION", active=True)
    authentication_classes = [MultiAuthentication]
    serializer_class = TipoPosseSerializer

    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)


class UsufrutoFeriasServidoresView(ListBaseView):
    """
    View dos servidores/membros de férias
    """

    queryset = Usufruct.objects.all()
    authentication_classes = [MultiAuthentication]
    serializer_class = UsufrutoFeriasSerializer
    full_text_index = (
        "activity__acquisition_period__employee__pessoa_fisica__nome__icontains",
    )

    def get_queryset(self):
        ano = self.request.GET.get("ano", None)
        mes = self.request.GET.get("mes", None)
        queryset = self.queryset.filter(
            status__in=[
                USU_NEW,
                USU_AUTORIZED_CI,
                USU_HOMOLOGATED,
                USU_ENJOYING,
                USU_ENJOYED,
                USU_SUBSTITUTE,
            ],
            activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in=[
                REGULAR_VACATIONS,
                INDIVIDUAL_VACATION,
            ],
        )
        dt_inicio_filter = Q()
        dt_fim_filter = Q()
        if ano:
            dt_inicio_filter &= Q(start_date__year=ano)
            dt_fim_filter &= Q(end_date__year=ano)
        if mes:
            dt_inicio_filter &= Q(start_date__month=mes)
            dt_fim_filter &= Q(end_date__month=mes)
        filters = dt_inicio_filter | dt_fim_filter
        queryset = queryset.filter(filters)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="ano", description="Ano", type=int),
            OpenApiParameter(name="mes", description="Mês", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View dos servidores/membros de férias
        """
        return self.list(request, *args, **kwargs)
