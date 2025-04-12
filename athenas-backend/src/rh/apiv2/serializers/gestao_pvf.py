from rest_framework import serializers

from apiv2.baseserializers import BaseSerializer
from rh.pvf.models import PortalRequest, PortalRequestHistory


class PortalRequestHistorySerializer(BaseSerializer):
    acao = serializers.SerializerMethodField()

    class Meta:
        model = PortalRequestHistory
        fields = ["acao", "grupo", "servidor", "data", "observacao"]
        extra_kwargs = {
            "grupo": {"source": "get_group_name"},
            "servidor": {"source": "employee"},
            "data": {"source": "date"},
            "observacao": {"source": "observation"},
        }

    def get_acao(self, instance):
        return {"id": instance.action, "display": instance.get_action_display()}


class PortalRequestSerializer(BaseSerializer):
    historicos = PortalRequestHistorySerializer(
        source="portalrequesthistory_set", many=True, read_only=True
    )
    situacao = serializers.SerializerMethodField()
    tipo_solicitacao = serializers.SerializerMethodField()

    class Meta:
        model = PortalRequest
        fields = [
            "id",
            "tipo_solicitacao",
            "mes_referencia",
            "situacao",
            "servidor",
            "aprovador",
            "dias_aguardando_aprovacao",
            "periodo_aquisitivo",
            "data_solicitacao",
            "historicos",
        ]
        extra_kwargs = {
            "servidor": {"source": "employee_name"},
            "aprovador": {"source": "approver_name"},
            "mes_referencia": {"source": "get_sending_reference"},
            "dias_aguardando_aprovacao": {"source": "days_awaiting_approval"},
            "periodo_aquisitivo": {"source": "acquisitive_period"},
            "data_solicitacao": {"source": "date"},
        }

    def get_situacao(self, instance):
        return {"id": instance.status, "display": instance.get_status_display()}

    def get_tipo_solicitacao(self, instance):
        return {
            "id": instance.portal_request_type,
            "display": instance.get_portal_request_type_display(),
        }
