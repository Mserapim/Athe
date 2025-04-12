from contrib.utils import getLogger
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rh.pvf.apiv2.utils.timesheet import get_request_progress_timesheet
from rh.pvf.const import MSG_SUCCESS_METHOD
from standard.models import JustificationItem
from rh.pvf.models import PointJustification, PortalRequest, SendingTimeSheet
from rest_framework import status
from django.db.models.query_utils import Q


log = getLogger(__name__)


class PVFReferenceTimeeSheetSerializer(serializers.Serializer):
    """
    classe serializer lista de referências disponiveis para realizar os envios folha ponto
    """

    reference = serializers.CharField()


class PVFJustificationItensSerializer(serializers.ModelSerializer):
    """
    classe serializer  da lista das justificativas do folha ponto
    """

    value_key = serializers.IntegerField(source="value")

    class Meta:
        model = JustificationItem
        fields = ["value_key", "name"]


class PVFPointJustificationSerializer(serializers.ModelSerializer):
    """
    classe serializer  das justificativas do folha ponto
    """

    reason_type_name = serializers.CharField(source="get_motivo_nome", required=False)
    canceled = serializers.BooleanField(source="cancelado", required=False)
    days = serializers.IntegerField(source="get_dias", required=False)

    class Meta:
        model = PointJustification
        fields = [
            "pk",
            "reason_type",
            "reason_type_name",
            "number_hours",
            "days",
            "start_date",
            "end_date",
            "observation",
            "attachment",
            "request",
            "canceled",
            "origem",
        ]

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["post"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst

    def perform_update(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            self.is_valid(raise_exception=True)
            self.save()
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["put"],
                    "data": self.data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst


class PVFSendTimeSheetSerializer(serializers.ModelSerializer):
    """
    classe serializer da solicitação de folha ponto
    """

    class Meta:
        model = SendingTimeSheet
        fields = []

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            if not get_request_progress_timesheet():
                instance = SendingTimeSheet.create(data.get("reference", None))
                rst.update(
                    success=True,
                    message="Registro criado com sucesso.",
                    data={
                        "pk": instance.pk,
                        "month": instance.reference_month,
                        "year": instance.reference_year,
                    },
                )
            else:
                rst.update(
                    message="Já existe uma solicitação de folha ponto em andamento."
                )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst

    def send(self, pk):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            instance = SendingTimeSheet.objects.get(pk=pk)
            instance.send()
            rst = {"success": True, "message": "Envio realizado como sucesso."}
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class PVFPendingTimeSheetSerializer(serializers.Serializer):
    """
    classe serializer da lista de pendências do folha ponto
    """

    type = serializers.CharField()
    value = serializers.CharField()


class PVFFolhaPontoAfastamentosSerializer(ModelSerializer):
    """
    classe serializer das solicitações de afastamentos abertos que não foram efetivadas
    """

    data_solicitacao = serializers.CharField(source="date")
    tipo_solicitacao = serializers.CharField(source="type_of_request")
    situacao = serializers.CharField(source="status_name")
    agendamentos = serializers.SerializerMethodField()

    class Meta:
        model = PortalRequest
        fields = [
            "id",
            "data_solicitacao",
            "tipo_solicitacao",
            "situacao",
            "agendamentos",
        ]

    def get_agendamentos(self, obj):
        id = self.context["request"].GET.get("id")
        folha_ponto = SendingTimeSheet.objects.get(pk=id)
        agendamento = []
        if hasattr(obj, "portalrequestusufruct"):
            atividades = obj.portalrequestusufruct.activity.filter()
            for atividade in atividades:
                usufrutos = atividade.usufructs.filter(
                    Q(
                        start_date__year=folha_ponto.reference_year,
                        start_date__month=folha_ponto.reference_month,
                    )
                    | Q(
                        end_date__year=folha_ponto.reference_year,
                        end_date__month=folha_ponto.reference_month,
                    )
                )
                for usufruto in usufrutos:
                    if usufruto.start_date:
                        agendamento.append(
                            {
                                "data_inicio": usufruto.start_date,
                                "data_fim": usufruto.end_date,
                            }
                        )
        else:
            agendamento.append(
                {
                    "data_inicio": obj.portalrequestabsence.start_date,
                    "data_fim": obj.portalrequestabsence.end_date,
                }
            )
        return agendamento
