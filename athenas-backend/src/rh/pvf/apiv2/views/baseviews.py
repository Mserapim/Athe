from apiv2.utils import response_api_view
from rh.pvf.apiv2.utils.base import expressao_query, get_lista_params
from rh.pvf.models import PortalRequest, PortalRequestHistory, PortalRequestSubstitute
from rh.pvf.apiv2.serializers.baseserializers import *
from rh.models import ConfigPeriodoCumulativoSubstituicao, Servidor, ServidorLotacao
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rest_framework.response import Response
from rh.pvf.apiv2.filters import (
    PVFRequestListFilterBackend,
    PVFMinhasSubstituicoesFilterBackend,
    PVFVendaSubstituicoesFilterBackend,
)
from drf_spectacular.utils import OpenApiParameter, extend_schema
from apiv2.baseviews import BaseViewSet, ListBaseView
from rest_framework.generics import RetrieveAPIView
from standard.models import Choice
from rh.models import PessoaFisica
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from contrib.middleware import set_current_user
from rh.pvf.apiv2.utils.mypendecies import my_pendecies_data
from rh.pvf.const import *
from rh.pvf.utils.validacoes import validar_substituto_afastamento
from django.db.models import Q
from contrib.utils import getLogger
import json

log = getLogger(__name__)


class BaseRequestViewSet(BaseViewSet):
    """
    View base para solicitações do VDF
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]

    def get(self, request, *args, **kwargs):
        """Retorna as solicitações"""
        return self.list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFRequestView(ListBaseView):
    """
    View das solicitações do vida funcional
    """

    queryset = PortalRequest.objects.all()
    serializer_class = PVFRequestSerializer
    filter_backends = (PVFRequestListFilterBackend,)
    full_text_index = (
        "approver__pessoa_fisica__nome__unaccent__icontains",
        "approver__pessoa_fisica__social_name__unaccent__icontains",
        "approver__matricula__icontains",
        "pk__iexact",
    )

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee)
        return self.filter_queryset(queryset)


class PVFRequestViewDetail(RetrieveAPIView):
    """
    View das solicitações do vida funcional
    """

    queryset = PortalRequest.objects.all()
    serializer_class = PVFRequestSerializer

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)


class PVFHistoryViewSet(BaseRequestViewSet):
    """
    View do histórico da solicitações do vida funcional
    """

    queryset = PortalRequestHistory.objects.filter()
    serializer_class = PVFHistorySerializer

    @action(detail=True, methods=["GET"])
    def request_histories(self, request, pk=None):
        queryset = self.queryset.filter(portal_request__pk=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)

    def get_queryset(self):
        return self.filter_queryset(self.queryset)


class PVFHistoricoAnexoView(ListBaseView):
    """
    View do histórico de anexos da solicitação
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id_solicitacao", description="Id da solicitação", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View do histórico de anexos da solicitação
        """
        id_solicitacao = self.request.GET.get("id_solicitacao")
        query_historicos = PortalRequestHistory.objects.filter(
            portal_request__pk=id_solicitacao
        )
        anexos_doc = []
        for historico in query_historicos:
            for anexo in historico.anexos.all():
                anexos_doc.append(
                    {
                        "id": anexo.pk,
                        "nome_arquivo": anexo.filename,
                        "origem": historico.get_origem,
                    }
                )
        return response_api_view(anexos_doc)


class PVFSubstituteViewSet(BaseRequestViewSet):
    """
    View dos substitutos da solicitação
    """

    queryset = PortalRequestSubstitute.objects.filter()
    serializer_class = PVFSubstituteSerializer

    @action(detail=True, methods=["GET"])
    def request_substitutes(self, request, pk=None):
        queryset = self.queryset.filter(
            portal_request__pk=pk, exercise__lotacao__electoral_zone=False
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)

    def get_queryset(self):
        return self.filter_queryset(self.queryset)


class PVFDesignationViewSet(BaseRequestViewSet):
    """
    View da Designação/Exercicio da tela de substitutos
    """

    queryset = ServidorLotacao.objects.filter(designacao=True)
    serializer_class = PVFDesignationSerializer

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        choices = Choice.objects.filter(
            name="VDF_OPTIONAL_SUBSTITUTE_LOCAL", active=True
        ).values_list("label")
        if employee.type_by_possession in ["MBR", "MEL", "MEC", "MCM"]:
            if validar_substituto_afastamento(employee):
                queryset = self.queryset.filter(
                    servidor=employee,
                    owner=True,
                    lotacao__electoral_zone=False,
                    movimentacao_posse__quadro__cargo__configs__replaceable=True,
                ).exclude(lotacao__pk__in=[int(x[0]) for x in choices])
            else:
                queryset = self.queryset.filter(
                    servidor=employee,
                    responsible=True,
                    owner=True,
                    lotacao__electoral_zone=False,
                    movimentacao_posse__quadro__cargo__configs__replaceable=True,
                ).exclude(lotacao__pk__in=[int(x[0]) for x in choices])
        else:
            queryset = self.queryset.filter(
                servidor=employee, movimentacao_posse__quadro__cargo__chefia=True
            )
        params = self.request.query_params.items()
        data = get_lista_params(params)
        _filter = self.consulta_data_designacao(data)
        query = expressao_query(_filter)
        if query:
            queryset = queryset.filter(query)
        return queryset

    def consulta_data_designacao(self, dados):
        _filtro = []
        if dados:
            for datas in dados:
                data_inicio = datetime.strptime(
                    formart_date_str(datas["start_date"]), "%d/%m/%Y"
                ).date()
                data_fim = datetime.strptime(
                    formart_date_str(datas["end_date"]), "%d/%m/%Y"
                ).date()
                _filtro.append(
                    Q(
                        data_vigencia_fim__isnull=True,
                        data_vigencia_inicio__lte=data_fim,
                    )
                    | Q(
                        data_vigencia_inicio__lte=data_fim,
                        data_vigencia_fim__gte=data_inicio,
                    )
                )
        return _filtro


class PVFPersonViewSet(BaseRequestViewSet):
    """
    View da config de pessoa física
    """

    queryset = PessoaFisica.objects.filter()
    serializer_class = PVFPersonSerializer
    full_text_index = ("nome__unaccent__icontains", "id__iexact")

    def get_queryset(self):
        return self.filter_queryset(self.queryset)

    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação"""
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        set_current_user(request.user)
        request.data.update(
            {
                "social_name": request.data.get("name"),
                "email_pessoal": "NAOINFORMADO@MPMT.MP.BR",
            }
        )
        serializer = self.get_serializer(data=request.data)
        response = serializer.perform_create()
        return Response(response, status=response["code"])


class PVFMyPendeciesView(ListBaseView):
    """
    View das minhas pendências
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    serializer_class = PVFTMyPendeciesSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista das minhas pendências
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        employee = Servidor.objects.get(user=self.request.user)
        data = my_pendecies_data(employee)
        paginated_data = self.paginate_queryset(data)
        if paginated_data is not None:
            data_serializer = self.serializer_class(paginated_data, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = self.serializer_class(paginated_data, many=True).data
        return response_api_view(data_serializer)


class PVFMinhasSubstituicoesView(ListBaseView):
    """
    View das Minhas Substituições
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    filter_backends = (PVFMinhasSubstituicoesFilterBackend,)
    serializer_class = PVFMinhasSubstituicoesSerializer
    queryset = MovimentacaoSubstituicao.objects.filter()

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="dt_inicio", description="Data início", type=str),
            OpenApiParameter(name="dt_fim", description="Data fim", type=str),
            OpenApiParameter(
                name="tipo_acao",
                description="Tipo de ação: 1 ou 2 (1=Substituto, 2=Substituído, vazio=todos)",
                type=int,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista das Minhas Substituições
        """

        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        servidor = Servidor.objects.get(user=self.request.user)
        query = self.queryset.filter(
            Q(place__classificacao__in=[1, 2]),
            Q(paid_out=False),
            Q(servidor=servidor) | Q(servidor_substituido=servidor),
            Q(indeferido=False),
            Q(designation_substituted__lotacao__classificacao__in=[1, 2]),
        )

        return self.filter_queryset(query)

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)


class PVFVendaSubstituicoesView(ListBaseView):
    """
    View de Venda de Cumulativo de Substituições
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    filter_backends = (PVFVendaSubstituicoesFilterBackend,)
    serializer_class = PVFVendaSubstituicoesSerializer
    queryset = MovimentacaoSubstituicao.objects.filter()

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="dt_inicio", description="Data início", type=str),
            OpenApiParameter(name="dt_fim", description="Data fim", type=str),
            OpenApiParameter(
                name="tipo_acao",
                description="Tipo de ação: 1 ou 2 (1=Substituto, 2=Substituído, vazio=todos)",
                type=int,
            ),
            OpenApiParameter(
                name="dt_ini_periodo", description="Data início do período", type=str
            ),
            OpenApiParameter(
                name="dt_fim_periodo", description="Data fim do período", type=str
            ),
            OpenApiParameter(
                name="dt_ini_abrangencia",
                description="Data início da abrangência",
                type=str,
            ),
            OpenApiParameter(
                name="dt_fim_abrangencia",
                description="Data fim da abrangência",
                type=str,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Lista ds Venda de Cumulativo de Substituições
        """

        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        servidor = Servidor.objects.get(user=self.request.user)
        query = self.queryset.filter(
            Q(place__classificacao__in=[1, 2]),
            Q(paid_out=False),
            Q(servidor=servidor) & ~Q(servidor_substituido=servidor),
            Q(indeferido=False),
            Q(designation_substituted__lotacao__classificacao__in=[1, 2]),
            Q(pvf_exercicio_cumulativos__isnull=True),
        )
        data_atual = datetime.today().date()
        config = ConfigPeriodoCumulativoSubstituicao.objects.filter(
            data_inicio_periodo__lte=data_atual, data_fim_periodo__gte=data_atual
        ).first()
        if config:
            query = query.filter(
                Q(data_inicio__gte=config.data_inicio_abrangencia)
                & Q(data_fim__lte=config.data_fim_abrangencia)
            )
        # query = (self.queryset.filter(place__classificacao__in=[1,2]
        #     ).filter(Q(servidor=servidor) & ~Q(servidor_substituido=servidor)
        #     ).filter(paid_out=False,indeferido=False)

        # )

        return self.filter_queryset(query)

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response_api_view(serializer.data)
