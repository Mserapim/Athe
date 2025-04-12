import traceback
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import rest_framework.permissions
from django.db import transaction
from contrib.middleware import set_current_user
from contrib.utils import getLogger

from diarias.models import (
    Beneficiario,
    FluxoViagem,
    HistoricoFluxoViagemBeneficiario,
    PassagemAeriaViagem,
    VeiculoPassageiro,
    Viagem,
)
from rh.pvf.utils.chefe_imediato import get_aprovador
from standard.models import Choice
from rh.models import Cargo

from apiv2.baseviews import ApiCore, ListBaseView, ApiDetailView
from diarias.apiv2.serializers.viagem import (
    HistoricoFluxoViagemBeneficiarioSerializer,
    PassagemAereaViagemSerializer,
    VeiculoPassageiroSerializer,
    ViagemSerializer,
)

from diarias.utils.historico import (
    buscar_historico_viagem,
    buscar_historico_beneficiario,
)
from diarias.utils.destinos_detalhado import buscar_destinos_detalhado
from diarias.utils.fluxo_movimentacao import benef_mover_etapa

import traceback
from diarias.utils.utils import validar_viagem_finalizar, validar_viagem_cancelar
from diarias.utils.notificacao_cancelamento import (
    enviar_email_cancelamento_beneficiario,
    enviar_email_cancelamento_daa,
    enviar_email_cancelamento_deplan,
    enviar_email_cancelamento_dg,
)
from menu_permissoes.models import UsuarioGrupo

log = getLogger(__name__)


class MinhasViagensApiList(ListBaseView):

    serializer_class = ViagemSerializer
    model = Viagem

    full_text_index = (
        "created_by__servidor__pessoa_fisica__social_name__unaccent__icontains",
        "beneficiarios__servidor__pessoa_fisica__nome__unaccent__icontains",
    )

    def get_queryset(self):
        user = self.request.user
        viagens = Viagem.objects.filter(
            Q(created_by=user)
            | Q(beneficiarios__servidor__user=user)
            | Q(
                beneficiarios__chefe_imediato__user=user, beneficiarios__fluxo__id=20
            )  # filtro de chefe imediato igual ao usuario logado e beneficiario guardando a ciencia do chefe imediato
        )

        if user.servidor.subordinados.all().exists():

            beneficiarios_sem_chefe = Beneficiario.objects.exclude(
                Q(viagem__in=viagens)
            ).filter(
                chefe_imediato__isnull=True,
                servidor__type_by_possession__in=[
                    "EFE",
                    "ECM",
                    "CMS",
                    "REQ",
                    "RCM",
                    "EFC",
                    "REX",
                    "EXT",
                ],  # Somente tipo servidor
                fluxo=20,  # fluxo do beneficiario guardando a ciencia do chefe imediato
            )

            beneficiarios_sem_chefe = [
                b for b in beneficiarios_sem_chefe if b.viagem.fluxo_atual.pk != 2
            ]  # Exclui viagens na situação "Rascunho"

            viagens_extra = []
            for beneficiario in beneficiarios_sem_chefe:
                try:
                    chefe_imediato = get_aprovador(beneficiario.servidor)
                    if chefe_imediato and chefe_imediato.user == user:
                        viagens_extra.append(beneficiario.viagem_id)
                except Exception as e:
                    erro_completo = traceback.format_exc()
                    log.error(erro_completo)

            if viagens_extra:
                viagens = viagens | Viagem.objects.filter(id__in=viagens_extra)

        return viagens.distinct().order_by("-data_inicio_viagem")

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        situacoes = self.request.GET.getlist("situacoes[]")
        tipos = self.request.GET.getlist("tipos_viagem[]")
        motivos = self.request.GET.getlist("motivos_viagem[]")
        finalidades = self.request.GET.getlist("finalidades[]")

        if situacoes and situacoes is not None:
            situacao_rascunho = Choice.objects.get(
                app_label="diarias",
                name="SITUACAO_SOLICITACAO_VIAGEM",
                label="Rascunho",
            )
            situacoes = list(map(int, situacoes))

            if situacao_rascunho.value in situacoes:
                queryset = queryset.filter(
                    Q(beneficiarios__isnull=True)
                    | Q(
                        beneficiarios__isnull=False,
                        beneficiarios__fluxo__situacao__in=situacoes,
                    )
                )

            else:
                queryset = queryset.filter(
                    beneficiarios__isnull=False,
                    beneficiarios__fluxo__situacao__in=situacoes,
                )

        if tipos and tipos is not None:
            queryset = queryset.filter(tipo_viagem__in=tipos)

        if motivos and motivos is not None:
            motivos = list(map(int, motivos))

            queryset = queryset.filter(motivo_viagem__in=motivos)

        if finalidades and finalidades is not None:
            finalidades = list(map(int, finalidades))

            queryset = queryset.filter(finalidade_viagem__in=finalidades)

        return queryset.distinct()


class ViagemApiCore(ApiCore):

    serializer_class = ViagemSerializer
    model = Viagem

    path_function_map = {
        "criar": "create",
        "editar": "update",
        "cancelar": "cancelar",
        "finalizar": "finalizar",
    }

    def cancelar(self, request, *args, **kwargs):
        resposta = {"code": 400, "datail": "Nada Feito"}

        try:

            set_current_user(request.user)
            instance = self.get_object()

            beneficiarios_ids = self.request.data.get("beneficiarios_ids", [])

            solicitante = instance.created_by
            usuario = request.user

            cancelador = usuario.servidor.pessoa_fisica.social_name

            beneficiarios = Beneficiario.objects.filter(id__in=beneficiarios_ids)

            validar_viagem_cancelar(
                viagem=instance,
                beneficiarios=beneficiarios,
                solicitante=solicitante,
                usuario=usuario,
            )

            fluxo_cancelado = FluxoViagem.objects.get(id=32)
            fluxo_cancelado_dg = FluxoViagem.objects.get(id=52)
            fluxo_cancelado_daa = FluxoViagem.objects.get(id=34)
            fluxo_cancelado_deplan = FluxoViagem.objects.get(id=35)

            beneficiarios_dg = []
            beneficiarios_daa = []
            beneficiarios_deplan = []

            fluxos_aguardando_empenho = [49, 50]

            # Move todos os beneficiarios de etapa
            with transaction.atomic():
                for beneficiario in beneficiarios:

                    if beneficiario.historico_fluxos.filter(fluxo__id=10).exists():
                        beneficiarios_deplan.append(beneficiario)
                    if beneficiario.historico_fluxos.filter(fluxo__id=8).exists():
                        benef_mover_etapa(beneficiario, fluxo_cancelado_daa.id)
                        beneficiarios_daa.append(beneficiario)
                    if beneficiario.historico_fluxos.filter(
                        fluxo__id__in=fluxos_aguardando_empenho
                    ).exists():
                        beneficiarios_dg.append(beneficiario)
                    else:
                        benef_mover_etapa(beneficiario, fluxo_cancelado.id)

            for beneficiario in beneficiarios:
                enviar_email_cancelamento_beneficiario(beneficiario, cancelador)

            if len(beneficiarios_daa) > 0:
                enviar_email_cancelamento_daa(beneficiarios_daa, cancelador)

            if len(beneficiarios_deplan) > 0:
                enviar_email_cancelamento_deplan(beneficiarios_deplan, cancelador)

            if len(beneficiarios_dg) > 0:
                enviar_email_cancelamento_dg(beneficiarios_dg, cancelador)

            resposta["datail"] = "Solicitação de viagem foi cancelada."
            resposta["code"] = 200

        except self.model.DoesNotExist:
            resposta["datail"] = "O objeto não existe ou já foi excluido"
        except Exception as e:
            log.error(e)
            erro_completo = traceback.format_exc()  # Captura o stack trace como string
            log.error(erro_completo)
            resposta["datail"] = (
                f"Erro ao tentar cancelar a solicitação da viagem - {e}"
            )

        return Response(resposta, status=resposta["code"])

    def finalizar(self, request, *args, **kwargs):
        resposta = {"code": 400, "datail": "Nada Feito"}

        try:

            set_current_user(request.user)
            instance = self.get_object()

            validar_viagem_finalizar(instance)

            # Move todos os beneficiarios de etapa
            with transaction.atomic():
                for beneficiario in instance.beneficiarios.all():
                    benef_mover_etapa(beneficiario)

            resposta["datail"] = "Solicitação de viagem concluída."
            resposta["code"] = 200

        except self.model.DoesNotExist:
            resposta["datail"] = "O objeto não existe ou já foi excluido"
        except Exception as e:
            log.error(e)
            erro_completo = traceback.format_exc()  # Captura o stack trace como string
            log.error(erro_completo)
            resposta["datail"] = (
                f"Erro ao tentar finalizar a solicitação da viagem - {e}"
            )

        return Response(resposta, status=resposta["code"])


class ViagemApiDetail(ApiDetailView):

    serializer_class = ViagemSerializer
    model = Viagem


class ViagensApiList(ListBaseView):

    serializer_class = ViagemSerializer
    model = Viagem

    full_text_index = (
        "created_by__servidor__pessoa_fisica__social_name__unaccent__icontains",
        "beneficiarios__servidor__pessoa_fisica__nome__unaccent__icontains",
    )

    def get_queryset(self):
        return Viagem.objects.filter()

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        situacoes = self.request.GET.getlist("situacoes[]")
        etapas = self.request.GET.getlist("etapas[]")
        tipos = self.request.GET.getlist("tipos_viagem[]")
        motivos = self.request.GET.getlist("motivos_viagem[]")
        finalidades = self.request.GET.getlist("finalidades[]")

        servidores = self.request.GET.getlist("servidores[]")

        if situacoes and situacoes is not None:
            situacao_rascunho = Choice.objects.get(
                app_label="diarias",
                name="SITUACAO_SOLICITACAO_VIAGEM",
                label="Rascunho",
            )
            situacoes = list(map(int, situacoes))

            if situacao_rascunho.value in situacoes:
                queryset = queryset.filter(
                    Q(beneficiarios__isnull=True)
                    | Q(
                        beneficiarios__isnull=False,
                        beneficiarios__fluxo__situacao__in=situacoes,
                    )
                )

            else:
                queryset = queryset.filter(
                    beneficiarios__isnull=False,
                    beneficiarios__fluxo__situacao__in=situacoes,
                )

        if etapas and len(etapas) > 0:
            queryset = queryset.filter(
                beneficiarios__isnull=False, beneficiarios__fluxo__etapa__in=etapas
            )

        if tipos and len(tipos) > 0:
            queryset = queryset.filter(tipo_viagem__in=tipos)

        if motivos and len(motivos) > 0:
            motivos = list(map(int, motivos))

            queryset = queryset.filter(motivo_viagem__in=motivos)

        if finalidades and len(finalidades) > 0:
            finalidades = list(map(int, finalidades))

            queryset = queryset.filter(finalidade_viagem__in=finalidades)

        if servidores and len(servidores) > 0:
            queryset = queryset.filter(beneficiarios__servidor__in=servidores)

        return queryset.distinct()


class ViagemPermissaoView(APIView):
    """
    Retorna se o usuario logado tem permissão para criar uma viagem
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Retorna se o usuario logado tempermissão para criar uma viagem
        """

        servidor = request.user.servidor

        grupo_admin = UsuarioGrupo.objects.get(nome="admin-suite")

        if servidor in grupo_admin.servidores.all():
            return Response({"result": True})

        # LISTA_POSSES_MEMBROS = [ 'MBR', 'MEL', 'MCM', 'MEC' ]

        # LISTA_CARGOS_PERMITIDOS = [12961, 12960, 12924, 12926, 12958, 12952, 12925]

        # if servidor.type_by_possession in LISTA_POSSES_MEMBROS:
        #     return Response({'result': True})

        # cargos = Cargo.objects.filter(
        #     quadro__active=True,
        #     quadro__movimentacaoposse__isnull=False,
        #     quadro__movimentacaoposse__ativo=True,
        #     quadro__movimentacaoposse__servidor=servidor
        # ).values_list('id', flat=True)

        # for cargo in cargos:
        #     if cargo in LISTA_CARGOS_PERMITIDOS:
        #         return Response({'result': True})

        LISTA_LOTACAOES = [52464, 52636, 52509]  # ID das Lotações GSI e DAA

        query = servidor.servidor_lotacao.filter(
            ativo=True, lotacao__in=LISTA_LOTACAOES
        )

        if query.exists():
            return Response({"result": True})
        return Response({"result": False})


class ViagemHistoricoView(ListBaseView):
    """
    View do histórico de fluxo de uma Viagem
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        viagem_id = request.query_params.get("viagem_id")
        viagem = Viagem.objects.get(pk=viagem_id)

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": buscar_historico_viagem(viagem),
        }

        return Response(res)


class ViagemBeneficiarioHistoricoView(ListBaseView):
    """
    View do histórico de fluxo de um Beneficiário
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        beneficiario_id = request.query_params.get("beneficiario_id")
        beneficiario = Beneficiario.objects.get(pk=beneficiario_id)

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": buscar_historico_beneficiario(beneficiario),
        }

        return Response(res)


class HistoricoFluxoViagemBeneficiarioView(ListBaseView):
    """
    View para retornar as observações e anexos de um HistoricoFluxoViagemBeneficiario dado o ID.
    """

    serializer_class = HistoricoFluxoViagemBeneficiarioSerializer
    model = HistoricoFluxoViagemBeneficiario

    def list(self, request):
        historico_id = request.query_params.get("historico_id")
        queryset = HistoricoFluxoViagemBeneficiario.objects.filter(id=historico_id)

        if not queryset.exists():
            raise ValueError("Histórico não encontrado.")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ObservacaoHistoricoFluxoBeneficiario(APIView):
    """
    View para retornar os campos 'obs' e 'feedback' de um HistoricoFluxoViagemBeneficiario dado o fluxo_id e beneficiario_id.

    Se o fluxo_id não for fornecido, a View busca o histórico do fluxo anterior ao fluxo atual do beneficiário.
    """

    def get(self, request, *args, **kwargs):
        try:
            beneficiario_id = request.query_params.get("beneficiario")
            fluxo_id = request.query_params.get("fluxo", None)

            if fluxo_id:
                historico = HistoricoFluxoViagemBeneficiario.objects.filter(
                    beneficiario_id=beneficiario_id, fluxo_id=fluxo_id
                ).last()
            else:
                historico = HistoricoFluxoViagemBeneficiario.objects.filter(
                    beneficiario_id=beneficiario_id
                ).order_by("-created_at")[1]

            if not historico:
                return Response(
                    {
                        "message": "Nenhum histórico foi encontrado para este beneficiário e fluxo"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            data = {
                "obs": historico.obs,
                "feedback": historico.feedback,
                "acao_por": historico.acao_por,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DestinosDetalhadoView(ListBaseView):
    """
    View das informações financeiras detalhadas de um Beneficiário sobre uma Viagem
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        beneficiario_id = request.query_params.get("beneficiario_id")
        beneficiario = Beneficiario.objects.get(pk=beneficiario_id)

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": buscar_destinos_detalhado(beneficiario),
        }

        return Response(res)


class PassagemAereaViagemView(ListBaseView):
    """
    View para retornar uma PassagemAeriaViagem dado o ID do destino.
    """

    serializer_class = PassagemAereaViagemSerializer
    model = PassagemAeriaViagem

    def list(self, request):
        destino_id = request.query_params.get("destinoId")
        queryset = PassagemAeriaViagem.objects.filter(destino_id=destino_id)

        if not queryset.exists():
            raise ValueError("Passagem aérea não encontrada.")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VeiculoPassageiroViagemView(ListBaseView):
    """
    View para retornar uma VeiculoPassageiro dado o ID do destino.
    """

    serializer_class = VeiculoPassageiroSerializer
    model = VeiculoPassageiro

    def list(self, request):
        destino_id = request.query_params.get("destinoId")
        queryset = VeiculoPassageiro.objects.filter(passageiro_id=destino_id)

        if not queryset.exists():
            raise ValueError("Relação veículo-passageiro não encontrada.")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
