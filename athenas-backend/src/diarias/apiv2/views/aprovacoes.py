from django.db import transaction
from contrib.middleware import set_current_user
from diarias.utils.aprovacoes import (
    adicionar_passagem_aerea,
    analisar_diarias_beneficiario,
    aprovar_beneficiario,
    aprovar_defin_excedente,
    atualizar_valor_deferido_diarias,
    dar_ciencia_cancelamento,
    dar_ciencia_chefe_imediato,
    mover_fluxo_especifico,
    verificar_destinos_e_mover_fluxo,
    salvar_veiculos_passageiros,
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from contrib.utils import getLogger

log = getLogger(__name__)


class CienciaChefeImediatoApiView(APIView):
    """
    View para ciência de chefe imediato de Beneficiario, salvar chefe_imediato
    e criar HistoricoAnexo segundo a ação.
    """

    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiario")
                ciencia_chefe = request.data.get("cienciaChefe")
                chefe_imediato = request.user.servidor

                dar_ciencia_chefe_imediato(
                    beneficiario_id, ciencia_chefe, chefe_imediato
                )

                return Response(
                    {"success": True, "message": "Ciência dada com sucesso."},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InformacaoAprovacaoApiView(APIView):
    """
    View para criar configurações de HistoricoFluxoViagemBeneficiario segundo análise dos seguintes fluxos:
        DG - Aguardando aprovador
        SUB ADM - Aguardando aprovador
        PGJ - Aguardando análise
        Assessoria da PGJ - Análise afastamentos
        Análise da PGJ - Análise afastamentos
    """

    def post(self, request, *arg, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiario")
                acao_deferimento = request.data.get("acaoDeferimento")
                obs = request.data.get("obs")
                feedback = request.data.get("feedback", None)

                aprovar_beneficiario(beneficiario_id, acao_deferimento, obs, feedback)

                return Response(
                    {
                        "success": True,
                        "message": "Observação e ação de deferimento salvas com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseQuantidadeDiariasApiView(APIView):
    """
    View para criar configurações de HistoricoFluxoViagemBeneficiario segundo análise dos seguintes fluxos:
        Assessoria da SUB JUR - Aguardando análise (fluxo_id = 24 ou 30)
        Assessoria da PGJ - Aguardando análise (fluxo_id = 28)
        Assessoria da SUB ADM - Aguardando análise (fluxo_id = 31 ou 33)
        Assessoria da DG - Aguardando análise (fluxo_id = 6)
    """

    def post(self, request, *arg, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiario")
                quantidade_deferida = request.data.get("quantidadeDeferida", None)
                fluxo_especifico = request.data.get("fluxoEspecifico", None)
                acomp_autoridade = request.data.get("acompanhandoAutoridade", None)
                if acomp_autoridade is not None:
                    if isinstance(
                        acomp_autoridade, str
                    ):  # Caso o valor seja uma string
                        acomp_autoridade = acomp_autoridade.lower() == "true"

                obs = request.data.get("obs")
                feedback = request.data.get("feedback", None)

                analisar_diarias_beneficiario(
                    beneficiario_id,
                    quantidade_deferida,
                    fluxo_especifico,
                    obs,
                    acomp_autoridade,
                    feedback,
                )

                return Response(
                    {
                        "success": True,
                        "message": "Quantidade de diárias e análise salvas com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseDaaPassagemAereaApiView(APIView):
    """
    View para criar configurações de PassagemAeriaViagem, PassagemAereaAnexo e HistoricoFluxoViagemBeneficiario
    segundo análise do DAA (fluxo_id = 8).
    """

    def post(self, request, *arg, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                destino_id = request.data.get("destino")
                empresa = request.data.get("empresa")
                aeroporto = request.data.get("aeroporto")
                numero_bilhete = request.data.get("numeroBilhete")
                data_hora_voo = request.data.get("dataHoraVoo")
                anexos = request.data.get("anexos", [])

                adicionar_passagem_aerea(
                    destino_id,
                    empresa,
                    aeroporto,
                    numero_bilhete,
                    data_hora_voo,
                    anexos,
                )
                verificar_destinos_e_mover_fluxo(destino_id)

                return Response(
                    {"success": True, "message": "Passagem aérea salva com sucesso."},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SalvarVeiculosPassageirosApiView(APIView):
    """
    View para criar a relação de motoristas e/ou veículos com destinos.
    """

    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                veiculo_data = request.data.get("veiculo")
                motorista_data = request.data.get("motorista")
                destinos = request.data.get("destinos")

                salvar_veiculos_passageiros(destinos, veiculo_data, motorista_data)

                return Response(
                    {
                        "success": True,
                        "message": "Veículo e passageiros salvos com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseExcedenteDefin(APIView):
    """
    View para criar configurações de HistoricoFluxoViagemBeneficiario segundo análise do fluxo:
        DEFIN - Excedente (fluxo_id = 27)
    """

    def post(self, request, *arg, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiario")
                gedoc = request.data.get("gedoc")
                quantidade_deferida = request.data.get("quantidadeDeferida", None)
                acao_deferimento = request.data.get("acaoDeferimento")
                anexos = request.data.get("anexos", [])

                aprovar_defin_excedente(
                    beneficiario_id,
                    gedoc,
                    quantidade_deferida,
                    acao_deferimento,
                    anexos,
                )

                return Response(
                    {
                        "success": True,
                        "message": "Quantidade de diárias, análise e anexos salvos com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseValorDeferidoBeneficiario(APIView):
    """
    View para editar valor deferido do Benenficiário e salvar configurações de HistoricoFluxoViagemBeneficiario segundo análise.
    """

    def post(self, request, *arg, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiarioID")
                valor_deferido = request.data.get("valorDeferido")

                atualizar_valor_deferido_diarias(beneficiario_id, valor_deferido)

                return Response(
                    {
                        "success": True,
                        "message": "Valor deferido atualizado com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CienciaCancelamentoDiaria(APIView):
    """
    View para criar configurações de HistoricoFluxoViagemBeneficiario segundo ciência de cancelamento da diária.
    """

    def post(self, request, *arg, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiarios_id = request.data.get("beneficiarios")

                for beneficiario_id in beneficiarios_id:
                    dar_ciencia_cancelamento(beneficiario_id)

                return Response(
                    {"success": True, "message": "Ciência dada com sucesso."},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MoverBeneficiariosDiariasApiView(APIView):
    """
    View para mover fluxo de Beneficiário segundo análise de ADMIN.
    """

    def post(self, request, *arg, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiarios = request.data.get("beneficiarios")
                fluxo_especifico = request.data.get("fluxoEspecifico", None)
                obs = request.data.get("obs")

                mover_fluxo_especifico(beneficiarios, fluxo_especifico, obs)

                return Response(
                    {"success": True, "message": "Fluxo alterado com sucesso."},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
