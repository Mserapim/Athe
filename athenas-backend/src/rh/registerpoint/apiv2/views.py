from datetime import datetime, timedelta
from apiv2.utils import response_api_view
from contrib.base_converter import str_to_bool
from contrib.utils import employee_from_user, getLogger
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from apiv2.baseviews import ApiCore, ListBaseView
from rh.folhaponto.folhaponto_import_justificativas import (
    ORIGEM_JUSTIFICATIVA_IMPORTACAO_TRIELLO,
)
from rh.pvf.apiv2.utils.approval import belongs_group_dgp
from rh.pvf.apiv2.utils.timesheet import get_data_type_by_possession_access
from rh.pvf.const import STS_EFFECTIVE
from rh.pvf.models import PointJustification
from rh.registerpoint.const import ORIGEM_JUSTIFICATIVA_FOLHA_PONTO
from rh.registerpoint.models import MarkPoint
from rh.registerpoint.apiv2.serializers import (
    FolhaPontoJustificativasSerializer,
    FolhaPontoLotacaoSerializer,
    FolhaPontoParamentroSerializer,
    FolhaPontoServidorSerializer,
    FolhaPontoTipoJustificativaSerializer,
    PVFRegisterPointSerializer,
    PVFLastRegistereSerializer,
)
from rest_framework import status
from rh.models import CargaHoraria, Lotacao, Servidor
from rest_framework.response import Response
from contrib.middleware import set_current_user
from apiv2.pagination import CustomPagination
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rh.registerpoint.utils.ponto import (
    dividir_intervalo_datas,
    folha_ponto_periodo,
    get_lotacoes_aprovador,
    get_responsavel,
    inicio_fim_competencia,
    marcacao_editavel,
    servidores_aprovador_portal,
    servidores_chefe_imediato,
    carga_horaria_diaria,
)
from standard.models import Choice, JustificationItem
from contrib.middleware import set_current_user
from django.db.models.query_utils import Q

from contrib.utils import employee_from_user, getLogger, DateUtils

log = getLogger(__name__)


class PVFRegisterPointViewSet(GenericViewSet):
    """
    View do registro de ponto
    """

    queryset = MarkPoint.objects.all()
    serializer_class = PVFRegisterPointSerializer

    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação"""
        return self.create(request, *args, **kwargs)

    def create(self, request):
        set_current_user(request.user)
        serializer_data = self.serializer_class().register_point(request)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFLastRegisterView(ListBaseView):
    """
    View da última batida de ponto
    """

    queryset = MarkPoint.objects.filter()
    serializer_class = PVFLastRegistereSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        employee = Servidor.objects.get(user=self.request.user)
        queryset = self.queryset.filter(employee=employee, day=datetime.now().date())

        return queryset

    def get_paginated_response(self, data):
        per_page = self.get_queryset().count()
        return Response(
            {
                "total": 1,
                "page": 1,
                "per_page": per_page,
                "navigation": {
                    "next": None,
                    "previous": None,
                },
                "results": data,
            }
        )


class FolhaPontoTipoDiaView(ListBaseView):
    """
    View tipo dia folha ponto
    """

    model = Choice
    serializer_class = FolhaPontoParamentroSerializer

    def get_queryset(self):
        queryset = self.model.objects.filter(name="TIPO_DIA")
        return queryset


class FolhaPontoServidoresView(ListBaseView):
    """
    View dos serviores folha ponto
    """

    model = Servidor
    serializer_class = FolhaPontoServidorSerializer
    full_text_index = (
        "pessoa_fisica__nome__unaccent__icontains",
        "matricula__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="lotacao_id", description="Lotacao", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View dos serviores folha ponto
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        servidor_logado = Servidor.objects.get(user=self.request.user)
        lotacao_id = self.request.GET.get("lotacao_id", None)
        perfil_dgp = belongs_group_dgp(servidor_logado)
        servidores_pk = []

        if perfil_dgp:
            queryset = self.model.objects.exclude(
                type_by_possession__in=["MEL", "MBR", "MEC"]
            )
            if lotacao_id:
                queryset = queryset.filter(
                    servidor_lotacao__lotacao__pk=lotacao_id
                ).distinct()
        else:
            servidores_pk = []
            servidores_pk.extend(servidores_aprovador_portal(servidor_logado))
            servidores_pk.extend(servidores_chefe_imediato(servidor_logado))

            if servidores_pk:
                queryset = self.model.objects.filter(pk__in=list(set(servidores_pk)))
            else:
                queryset = self.model.objects.filter(pk=servidor_logado.pk)

        queryset = queryset.order_by("-ativo", "pessoa_fisica__nome")
        return queryset


class FolhaPontoMarcacoesView(ListBaseView):
    """
    View das marcações do ponto
    """

    model = MarkPoint
    full_text_index = ()

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(
                name="servidor_id", description="id do Servidor", type=int
            ),
            OpenApiParameter(name="inicio", description="período inicio", type=str),
            OpenApiParameter(name="fim", description="período fim", type=str),
            OpenApiParameter(name="mes", description="competência mês", type=int),
            OpenApiParameter(name="ano", description="competência ano", type=int),
            OpenApiParameter(name="tipos_dia[]", description="Tipo dia", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View das marcacoes do ponto
        """
        set_current_user(request.user)
        dt_inicio = request.GET.get("inicio", None)
        dt_fim = request.GET.get("fim", None)
        mes = request.GET.get("mes", None)
        ano = request.GET.get("ano", None)
        servidor_id = request.GET.get("servidor_id", None)
        tipos_dia = list(map(int, request.GET.getlist("tipos_dia[]", [])))
        order_by = request.GET.get("order_by", None)

        inicio_competencia, fim_competencia = inicio_fim_competencia(mes, ano)
        inicio = (
            datetime.strptime(dt_inicio, "%Y-%m-%d").date()
            if dt_inicio
            else inicio_competencia
        )
        fim = (
            datetime.strptime(dt_fim, "%Y-%m-%d").date() if dt_fim else fim_competencia
        )
        servidor = (
            Servidor.objects.get(pk=servidor_id)
            if servidor_id
            else employee_from_user(request.user)
        )
        if servidor.type_by_possession in [
            "MBR",
            "MEL",
            "MEC",
            "MCM",
            "MBR2",
            "MEL2",
            "MEC2",
            "MCM2",
        ]:
            return Response(
                {"message": "Membros não possuem folha ponto.", "data": []}, status=200
            )
        try:
            dados_ponto = folha_ponto_periodo(
                inicio, fim, servidor, tipos_dia=tipos_dia
            )
            if order_by:
                dados_ponto = self.ordenar_dados(dados_ponto, order_by)

            exportar = request.GET.get("exportar", None)
            if exportar:
                sincrono = str_to_bool(request.GET.get("sincrono", "false"))
                colunas = request.GET.getlist("colunas[]", [])
                return self.exportar_arquivo(exportar, colunas, sincrono, dados_ponto)

        except Exception as e:
            log.exception(e)
            return Response({"message": str(e), "code": 400}, status=400)
        return response_api_view(dados_ponto)

    def ordenar_dados(self, dados, order_by):
        """
        Ordena os dados já processados com base em order_by.
        """

        def obter_valor_para_ordenacao(item, field):
            """
            Obtém o valor do campo para ordenação, tratando valores None e listas.
            """
            value = item.get(field, None)
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            return (value is not None, str(value))

        if not order_by:
            return dados

        order_fields = order_by.replace(" ", "").split(",")

        for field in order_fields:
            reverse = field.startswith("-")
            clean_field = field.lstrip("-")
            try:
                dados.sort(
                    key=lambda x: obter_valor_para_ordenacao(x, clean_field),
                    reverse=reverse,
                )
            except Exception as e:
                log.warning(f"Erro ao ordenar pelo campo '{clean_field}': {e}")
                continue

        return dados


class FolhaPontoCoreView(ApiCore):
    """
    Atualizar certificado digital do esocial
    """

    model = MarkPoint

    path_function_map = {
        "ignorar-batida": "ignorar_batida",
    }

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"marcacao_id": {"type": "integer"}},
            },
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Descrição da operação POST

        executa uma função conforme o path da requisição
        """
        return super(FolhaPontoCoreView, self).post(request, args, kwargs)

    def ignorar_batida(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}

        marcacao_id = request.data.get("marcacao_id")
        if marcacao_id:
            try:
                marcacao = MarkPoint.objects.get(pk=marcacao_id)
                servidor_logado = employee_from_user(request.user)
                servidor = marcacao.employee
                perfil_dgp = True if belongs_group_dgp(servidor_logado) else False
                responsavel = get_responsavel(marcacao.employee)
                editavel = marcacao_editavel(
                    perfil_dgp,
                    responsavel,
                    servidor_logado,
                    servidor,
                    marcacao.marcacao.date(),
                )
                if editavel:
                    marcacao.marcacao_valida = not marcacao.marcacao_valida
                    marcacao.save()
                    resposta.update(resposta="Marcação atualizada com sucesso.")
                else:
                    resposta.update(
                        code=400,
                        resposta="Marcação não pode ser alterada porque já existe um envio de folha de ponto para a competência.",
                    )
            except Exception as e:
                log.exception(e)
                resposta.update(code=500, resposta="{}".format(e))
        else:
            resposta.update(
                code=400, resposta="Informe o id da marcação antes de continuar."
            )

        return Response(resposta, status=resposta["code"])


class FolhaPontoJustificativasView(ListBaseView):
    """
    View das justificativas do folha ponto
    """

    model = PointJustification
    serializer_class = FolhaPontoJustificativasSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="servidor_id", description="Id do servidor ", type=int
            ),
            OpenApiParameter(name="inicio", description="data inicio", type=str),
            OpenApiParameter(name="fim", description="data fim", type=str),
            OpenApiParameter(name="mes", description="Mês", type=int),
            OpenApiParameter(name="ano", description="Ano", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View das justificativas do folha ponto
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        id_servidor = self.request.GET.get("servidor_id", user.servidor.pk)
        dt_inicio = self.request.GET.get("inicio")
        dt_fim = self.request.GET.get("fim")
        ano = self.request.GET.get("ano")
        mes = self.request.GET.get("mes")

        inicio_competencia, fim_competencia = inicio_fim_competencia(mes, ano)
        dt_inicio = (
            DateUtils.str_to_date(dt_inicio, format="%Y-%m-%d")
            if dt_inicio
            else inicio_competencia
        )
        dt_fim = (
            DateUtils.str_to_date(dt_fim, format="%Y-%m-%d")
            if dt_fim
            else fim_competencia
        )
        servidor = Servidor.objects.get(pk=id_servidor)

        queryset = self.model.objects.filter(
            employee=servidor,
            cancelado=False,
            origem__in=[
                ORIGEM_JUSTIFICATIVA_FOLHA_PONTO,
                ORIGEM_JUSTIFICATIVA_IMPORTACAO_TRIELLO,
            ],
            start_date__lte=dt_fim,
            end_date__gte=dt_inicio,
        )
        return queryset


class FolhaPontoJustificativaCoreView(ApiCore):
    """
    Ações da api de justificativas
    """

    model = PointJustification
    serializer_class = FolhaPontoJustificativasSerializer

    path_function_map = {
        "criar": "create",
        "cancelar": "cancelar",
    }

    def create(self, request, *args, **kwargs):
        set_current_user(request.user)
        data = self.tratar_dados_horas(request.data, request.user.servidor.pk)
        if not data.get("servidor_id"):
            data["servidor_id"] = request.user.servidor.pk

        data_list = dividir_intervalo_datas(data)
        for data_obj in data_list:
            serializer = self.get_serializer(data=data_obj)
            response = serializer.perform_create()
        return Response(response, status=response["code"])

    def cancelar(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}

        justiticativa_id = request.data.get("justificativa_id")
        if justiticativa_id:
            try:
                justificativa = PointJustification.objects.get(pk=justiticativa_id)
                if justificativa.origem == ORIGEM_JUSTIFICATIVA_FOLHA_PONTO:
                    justificativa.cancelado = True
                    justificativa.save()
                    resposta.update(resposta="Justificativa cancelada com sucesso.")
                else:
                    resposta.update(
                        code=400, resposta="Não foi possível cancelar a justificativa."
                    )
            except Exception as e:
                log.exception(e)
                resposta.update(code=500, resposta="{}".format(e))
        else:
            resposta.update(
                code=400, resposta="Informe a justificativa_id antes de continuar."
            )

        return Response(resposta, status=resposta["code"])

    def tratar_dados_horas(self, data, servidor_id):
        """
        trata os dados recebido
        Args:
            request (Request): O objeto 'data' contendo os dados a serem tratados.
        Returns:
            dict: Os dados tratados.
        """
        data_inicio = data.get("data_inicio")
        data_fim = data.get("data_fim")
        if data.get("horas") != None:
            data["data_fim"] = data["data_inicio"]
        elif servidor_id and data_inicio:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

            jornadas_trabalho = CargaHoraria.objects.filter(
                servidor_id=servidor_id,
                data_inicio__lte=data_inicio,
                jornada_trabalho__isnull=False,
            ).order_by("-data_inicio")
            if jornadas_trabalho.exists():
                total_horas = 0
                delta = timedelta(days=1)
                dia = data_inicio
                while dia <= data_fim:
                    horas_do_dia = carga_horaria_diaria(jornadas_trabalho, dia)
                    total_horas += horas_do_dia
                    dia += delta

                horas = total_horas
                minutos = (total_horas - int(total_horas)) * 60
                data["horas"] = f"{int(horas):02}:{int(minutos):02}"

        else:
            data["horas"] = "00:00"
        return data


class FolhaPontoTipoJustificativaView(ListBaseView):
    """
    View dos tipos de justificativas
    """

    model = JustificationItem
    serializer_class = FolhaPontoTipoJustificativaSerializer
    full_text_index = ("name__unaccent__icontains",)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="servidor_id", description="Id do servidor ", type=int
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View das justificativas do folha ponto
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        id_servidor = self.request.GET.get("servidor_id", user.servidor.pk)
        servidor = Servidor.objects.get(pk=id_servidor)
        list_pks = get_data_type_by_possession_access(servidor.type_by_possession)
        queryset = self.model.objects.filter(pk__in=list_pks, exibir_folha_ponto=True)
        return queryset


class FolhaPontoLotacaoView(ListBaseView):
    """
    View das lotacoes por perfil aprovador do folha ponto
    """

    model = Lotacao
    serializer_class = FolhaPontoLotacaoSerializer
    full_text_index = ("nome__unaccent__icontains",)

    def get_queryset(self):
        user = self.request.user
        servidor = Servidor.objects.get(pk=user.servidor.pk)
        perfil_dgp = True if belongs_group_dgp(servidor) else False
        queryset = self.model.objects.all()
        if not perfil_dgp:
            lotacoes_pk = get_lotacoes_aprovador(servidor)
            queryset = self.model.objects.filter(pk__in=lotacoes_pk)
        return queryset


class PermissaoAdicionarJustificativaView(APIView):
    """
    API para verificar se o usuário logado tem permissão para adicionar justificativa.
    """

    def get(self, request, *args, **kwargs):
        try:
            servidor_logado = Servidor.objects.get(user=request.user)
        except Servidor.DoesNotExist:
            return Response(
                {"success": False, "message": "Servidor não encontrado."}, status=404
            )

        if belongs_group_dgp(servidor_logado):
            return Response({"success": True, "pode_adicionar_justificativa": True})

        if servidor_logado.responsible().filter(lotacao__portal_approver=True).exists():
            return Response({"success": True, "pode_adicionar_justificativa": True})

        if servidor_logado.subordinados.filter(ativo=True).exists():
            return Response({"success": True, "pode_adicionar_justificativa": True})

        return Response({"success": True, "pode_adicionar_justificativa": False})
