from contrib.daterange import NewDateRange
from rest_framework import serializers
from rh.pvf.models import PVFSolicitacaoCreditoFolga
from contrib.utils import getLogger
from rest_framework import serializers
from rh.pvf.const import MSG_SUCCESS_METHOD
from rest_framework import status


log = getLogger(__name__)


class PVFSolicitacaoFolgaSerializer(serializers.ModelSerializer):
    """
    classe serializer para criar/editar solicitações de folgas
    """

    dias = serializers.SerializerMethodField()
    tipo_folga_display = serializers.SerializerMethodField()

    class Meta:
        model = PVFSolicitacaoCreditoFolga
        fields = [
            "data_inicio",
            "data_fim",
            "anexo",
            "tipo_folga",
            "dias",
            "tipo_folga_display",
        ]

    def get_dias(self, obj):
        if hasattr(obj, "data_inicio") and hasattr(obj, "data_fim"):
            return NewDateRange(obj.data_inicio, obj.data_fim).days
        return 0

    def get_tipo_folga_display(self, obj):
        if hasattr(obj, "tipo_folga"):
            return obj.get_tipo_folga_display()
        return None

    def perform_create(self):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            request = self.context.get("request")
            self.is_valid(raise_exception=True)
            self.Meta.model.create(request.data)
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
            self.Meta.model.update(request.data, instance)
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
