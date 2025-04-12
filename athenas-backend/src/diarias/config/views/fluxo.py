from django.db import transaction
from contrib.middleware import set_current_user

from diarias.config.diarias import FluxoDiarias
from diarias.config.serializers.fluxo import (
    FluxoViagemLeituraSerializer,
    FluxoViagemSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView

from diarias.models import FluxoViagem


class FluxoViagemView(ListBaseView):
    """
    View da lista de Fluxos de Aprovação de Diarias
    """

    permission_classes = [IsAuthenticated]
    queryset = FluxoViagem.objects.filter().order_by("ordem")
    serializer_class = FluxoViagemLeituraSerializer
    full_text_index = ("nome__icontains",)


class FluxoViagemDetailView(ApiDetailView):
    """
    View do detalhe de um Fluxo Viagem
    """

    model = FluxoViagem
    serializer_class = FluxoViagemLeituraSerializer


class FluxoViagemApicoreView(ApiCore):
    """
    View para criar, editar e apagar configurações de FluxoViagem
    """

    model = FluxoViagem
    serializer_class = FluxoViagemSerializer

    def exclude(self, request, *args, **kwargs):
        resposta = {"code": 200, "detail": "Nada Feito"}

        try:
            set_current_user(request.user)
            instance = self.get_object()
            instance.condicionais.all().delete()
            instance.delete()
            resposta["detail"] = "Item Excluído com Sucesso"

        except self.model.DoesNotExist:
            resposta["detail"] = "O objeto não existe ou já foi excluído"
        except Exception as e:
            resposta["code"] = 500
            resposta["detail"] = f"Erro ao tentar excluir o item - {str(e)}"

        return Response(resposta, status=resposta["code"])


class EtapasDiariasView(ListBaseView):
    """
    View da lista de Etapas de um Fluxo
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": FluxoDiarias().buscar_todas_etapas(),
        }

        return Response(res)


class SituacoesDiariasView(ListBaseView):
    """
    View da lista de Situações de um Fluxo
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": FluxoDiarias().buscar_todas_situacoes(),
        }

        return Response(res)


class CondicionaisDiariasView(ListBaseView):
    """
    View da lista de Condicionais de um Fluxo
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": FluxoDiarias().buscar_todas_condicionais(),
        }

        return Response(res)


class FluxoViagemAtualizarOrdemView(APIView):
    """
    View para atualizar a ordem dos fluxos de viagem
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = data = request.data.get("updates", [])
        try:
            set_current_user(request.user)
            with transaction.atomic():
                FluxoViagem.objects.all().update(ordem=None)
                for item in data:
                    fluxo = FluxoViagem.objects.get(id=item["id"])
                    fluxo.ordem = item["novaOrdem"]
                    fluxo.save()
            return Response(
                {"detail": "Ordem atualizada com sucesso!"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
