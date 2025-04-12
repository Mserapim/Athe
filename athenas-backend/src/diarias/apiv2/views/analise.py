from django.db import transaction

from apiv2.baseviews import ApiCore
from contrib.middleware import set_current_user
from diarias.utils.fluxo_movimentacao import benef_mover_etapa
from diarias.utils.historico import clonar_ultimo_historico
from ged.models import Arquivo
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from diarias.apiv2.serializers.analise import AnaliseCeafSerializer
from diarias.models import (
    Beneficiario,
    HistoricoAnexo,
    HistoricoFluxoViagemBeneficiario,
)
from diarias.utils.aprovacoes import (
    receber_beneficarios,
    adicionar_nota_liquidacao,
    analise_ordem_bancaria,
    analise_empenho,
)

from contrib.utils import getLogger

log = getLogger(__name__)


class AnaliseCeafApiCore(ApiCore):
    """
    View para criar configurações de HistoricoFluxoViagemBeneficiario segundo análise do CEAF
    """

    serializer_class = AnaliseCeafSerializer
    model = HistoricoFluxoViagemBeneficiario


class AnaliseEmpenhoDeplanApiView(APIView):
    """
    View para salvar numero_empenho de Beneficiario e criar HistoricoAnexo segundo análise do Deplan.
    """

    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiario")
                numero_empenho = request.data.get("numero_empenho")
                empenho_liberado = request.data.get("empenho_liberado")
                anexos = request.data.get("anexos", [])

                analise_empenho(
                    beneficiario_id, numero_empenho, anexos, empenho_liberado
                )

                return Response(
                    {
                        "success": True,
                        "message": "Número de empenho e anexos salvos com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseNotaLiquidacaoDefinApiView(APIView):
    """
    View para análise de Viagem e de Beneficiario segundo o Defin.
    """

    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiario")
                numero_nota_liquidacao = request.data.get("numero_nota_liquidacao")
                anexos = request.data.get("anexos", [])

                adicionar_nota_liquidacao(
                    beneficiario_id, numero_nota_liquidacao, anexos
                )

                return Response(
                    {
                        "success": True,
                        "message": "Número da nota de liquidação e anexos salvos com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnaliseOrdemBancariaDefinApiView(APIView):
    """
    View para salvar numero_ordem_bancaria de Beneficiario e criar HistoricoAnexo segundo análise do Defin.
    """

    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                beneficiario_id = request.data.get("beneficiario")
                numero_ordem_bancaria = request.data.get("numero_ordem_bancaria")
                anexos = request.data.get("anexos", [])
                data_pagamento = request.data.get("data_pagamento", None)

                analise_ordem_bancaria(
                    beneficiario_id, numero_ordem_bancaria, anexos, data_pagamento
                )

                return Response(
                    {
                        "success": True,
                        "message": "Número da ordem bancária e anexos salvos com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReceberBeneficiariosApiView(APIView):
    """
    View para receber Beneficiarios e criar HistoricoAnexo segundo análise do Defin, Deplan e DG.
    """

    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        try:
            with transaction.atomic():
                viagem_id = request.data.get("viagem")

                receber_beneficarios(viagem_id)

                return Response(
                    {
                        "success": True,
                        "message": "Beneficiários recebidos com sucesso.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            log.exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
