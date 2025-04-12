from apiv2.baseviews import ApiCore, ListBaseView, ApiDetailView

from diarias.apiv2.serializers.destino import DestinoSerializer
from diarias.models import (
    Beneficiario,
    Destino,
    EventoBeneficiario,
    PassagemAeriaViagem,
    VeiculoPassageiro,
)

from contrib.utils import getLogger

from contrib.middleware import set_current_user
from rest_framework.response import Response
from diarias.utils.utils import clonar_destino
from rest_framework.views import APIView
from rest_framework import status
from standard.models import Choice
from django.db import transaction
from django.db.models import Exists, OuterRef, Q

log = getLogger(__name__)


class DestinosApiList(ListBaseView):

    serializer_class = DestinoSerializer
    model = Destino

    def get_queryset(self):
        beneficiario = self.request.GET.get("beneficiario", None)
        viagem = self.request.GET.get("viagem", None)
        fluxos_cancelados = [
            21,
            32,
        ]  # IDs dos fluxos que representam status "cancelado"

        if beneficiario:
            queryset = Destino.objects.filter(beneficiario__pk=beneficiario)

        if viagem:
            queryset = Destino.objects.filter(beneficiario__viagem__id=viagem).exclude(
                beneficiario__fluxo__id__in=fluxos_cancelados
            )

        queryset = queryset.order_by("data")

        return queryset

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        analise_daa = self.request.GET.get("analise_daa", None)
        com_motorista = self.request.GET.get("com_motorista", None)
        veiculo_daa = self.request.GET.get("veiculo_daa", None)

        if analise_daa is not None:
            passagem_aerea_exists = PassagemAeriaViagem.objects.filter(
                destino=OuterRef("pk")
            )
            veiculo_passageiro_exists = VeiculoPassageiro.objects.filter(
                passageiro=OuterRef("pk")
            )

            queryset = queryset.annotate(
                has_passagem_aerea=Exists(passagem_aerea_exists),
                has_veiculo_passageiro=Exists(veiculo_passageiro_exists),
            )

            if analise_daa.lower() == "true":
                queryset = queryset.filter(
                    Q(has_passagem_aerea=True) | Q(has_veiculo_passageiro=True)
                )
            elif analise_daa.lower() == "false":
                queryset = queryset.filter(
                    Q(has_passagem_aerea=False) & Q(has_veiculo_passageiro=False)
                )

        if com_motorista is not None:
            if com_motorista.lower() == "true":
                queryset = queryset.filter(com_motorista=True)
            elif com_motorista.lower() == "false":
                queryset = queryset.filter(com_motorista=False)

        if veiculo_daa is not None:
            if veiculo_daa.lower() == "true":
                queryset = queryset.filter(veiculo_daa=True)
            elif veiculo_daa.lower() == "false":
                queryset = queryset.filter(veiculo_daa=False)

        return queryset


class DestinosApiCore(ApiCore):

    serializer_class = DestinoSerializer
    model = Destino

    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
        "clonar": "clonar",
    }

    def clonar(self, request, *args, **kwargs):
        resposta = {"code": 200, "datail": "Nada Feito"}

        try:
            set_current_user(request.user)
            instance = self.get_object()

            beneficiarios_id = request.data.get("beneficiarios")
            if beneficiarios_id:
                for beneficiario in Beneficiario.objects.filter(
                    pk__in=beneficiarios_id
                ):
                    clonar_destino(instance, beneficiario)
                resposta["datail"] = "Destino Clonado com sucesso"
            else:
                resposta["datail"] = "Lista de beneficiarios não informada"

        except self.model.DoesNotExist:
            resposta["datail"] = "Destino Não encontrado"
            resposta["code"] = 400
        except Exception as e:
            resposta["datail"] = f"Erro ao tentar clonar o destino - {e}"
            resposta["code"] = 400

        return Response(resposta, status=resposta["code"])

    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        situacao_rascunho = Choice.objects.get(
            app_label="diarias", name="SITUACAO_SOLICITACAO_VIAGEM", label="Rascunho"
        )

        if instance.beneficiario.fluxo.situacao != situacao_rascunho.value:
            return Response(
                {
                    "message": "Não é possível editar o destino após o envio da solicitação"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()

                with transaction.atomic():
                    serializer.instance.eventos.clear()
                    evento_id = request.data.get("evento")
                    evento = EventoBeneficiario.objects.get(id=evento_id)
                    evento.destinos.add(serializer.instance)

                return Response(serializer.data)
            except Exception as e:

                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.message, status=status.HTTP_400_BAD_REQUEST)


class DestinoDetailView(ApiDetailView):

    serializer_class = DestinoSerializer
    model = Destino


class DestinoCloneLoteView(APIView):

    def post(self, request, format=None):
        beneficiario_base = request.data.get("beneficiario_base")
        beneficiarios = request.data.get("beneficiarios")

        try:
            set_current_user(request.user)

            destinos = Destino.objects.filter(beneficiario__pk=beneficiario_base)
            beneficiarios = Beneficiario.objects.filter(pk__in=beneficiarios)

            for destino in destinos:
                for beneficiario in beneficiarios:
                    clonar_destino(destino, beneficiario)

            return Response(
                {"message": "Destinos Clonados"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            log.error(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
