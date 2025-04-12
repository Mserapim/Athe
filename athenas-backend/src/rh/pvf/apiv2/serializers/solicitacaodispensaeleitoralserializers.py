from datetime import datetime

from rest_framework import serializers, status

from rh.pvf.models import PVFSolicitacaoCreditoDispensaEleitoral
from rh.pvf.const import MSG_SUCCESS_METHOD

from contrib.utils import getLogger


log = getLogger(__name__)


class PVFSolicitacaoDispensaEleitoralSerializer(serializers.ModelSerializer):
    """
    Classe serializer para criar/editar solicitações de crédito de dispensa eleitoral
    """

    dias = serializers.SerializerMethodField()
    tipo_solicitacao_display = serializers.SerializerMethodField()
    solicitante_display = serializers.SerializerMethodField()
    data_solicitacao = serializers.SerializerMethodField()
    nome_anexo = serializers.SerializerMethodField()
    obs_aprovador = serializers.SerializerMethodField()

    class Meta:
        model = PVFSolicitacaoCreditoDispensaEleitoral
        fields = [
            "dias",
            "tipo_solicitacao_display",
            "solicitante_display",
            "data_inicio",
            "data_fim",
            "observacao",
            "data_solicitacao",
            "anexo",
            "nome_anexo",
            "obs_aprovador",
        ]

    def get_dias(self, obj):
        return obj.get_qnt_dias() if hasattr(obj, "get_qnt_dias") else ""

    def get_tipo_solicitacao_display(self, obj):
        return (
            obj.get_request_type_display()
            if hasattr(obj, "get_request_type_display")
            else ""
        )

    def get_solicitante_display(self, obj):
        return (
            f"{obj.employee.matricula} - {obj.employee.pessoa_fisica.nome}"
            if hasattr(obj, "employee")
            else ""
        )

    def get_data_solicitacao(self, obj):
        return obj.date if hasattr(obj, "date") else None

    def get_nome_anexo(self, obj):
        return obj.anexo.filename if hasattr(obj, "anexo") and obj.anexo else ""

    def get_obs_aprovador(self, obj):
        if (
            hasattr(obj, "portalrequesthistory_set")
            and obj.portalrequesthistory_set.exists()
        ):
            query = obj.portalrequesthistory_set.filter(
                observation__isnull=False
            ).exclude(observation="")
            if query.exists():
                texto = ""
                for historico in query:
                    if texto == "":
                        texto = f"{historico.date.date().strftime('%d/%m/%Y')}: {historico.observation}"
                    else:
                        texto = f"{texto} / {historico.date.date().strftime('%d/%m/%Y')}: {historico.observation}"
                return texto
        return ""

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            request = self.context.get("request")
            self.is_valid(raise_exception=True)
            self.Meta.model.criar(request.data)
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
            request = self.context.get("request")
            self.is_valid(raise_exception=True)
            self.Meta.model.reenviar(request.data, instance)
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
