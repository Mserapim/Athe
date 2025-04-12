from contrib.utils import getLogger
from rest_framework import serializers
from rh.pvf.const import MSG_SUCCESS_METHOD
from rh.pvf.models import ShiftManager
from rest_framework import status

from rh.pvf.utils.custom_exception import LinkException


log = getLogger(__name__)


class PVFShiftManagerSerializer(serializers.ModelSerializer):
    """Class Serializer da escala de plantões servidores"""

    status = serializers.IntegerField(source="get_status", required=False)
    status_name = serializers.CharField(source="get_status_nome", required=False)
    comarca = serializers.SerializerMethodField()
    lotacao_titular = serializers.SerializerMethodField()
    criado_por = serializers.SerializerMethodField()
    anexo_display = serializers.SerializerMethodField(required=False)

    titulo_campo = {
        "status_name": "Situação",
        "type_shift_label": "Tipo de plantão",
        "employee_name": "Servidor",
        "comarca": "Comarca",
        "workplace_name": "Lotação",
        "lotacao_titular": "Lotação titular",
        "days": "Qtde dias",
        "start_date": "Data início",
        "end_date": "Data fim",
        "criado_por": "Criado por",
    }

    class Meta:
        model = ShiftManager
        fields = [
            "pk",
            "owner",
            "workplace",
            "workplace_name",
            "type_shift",
            "type_shift_label",
            "employee",
            "employee_name",
            "days",
            "start_date",
            "end_date",
            "status",
            "status_name",
            "comarca",
            "lotacao_titular",
            "criado_por",
            "observacao",
            "anexo",
            "anexo_display",
        ]

    def get_comarca(self, obj):
        if obj.workplace.localidade.comarca:
            return obj.workplace.localidade.comarca.nome
        return None

    def get_lotacao_titular(self, obj):
        if obj.employee.workplace_current:
            return obj.employee.workplace_current.nome
        return None

    def get_criado_por(self, obj):
        if obj.owner:
            return obj.owner.pessoa_fisica.nome
        return None

    def get_anexo_display(self, obj):
        if obj.anexo:
            return obj.anexo.filename
        return None

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
            self.linkException(instance)
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

    def perform_delete(self, instance):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_200_OK,
        }
        try:
            self.linkException(instance)
            instance.delete()
            rst.update({"success": True, "message": MSG_SUCCESS_METHOD["delete"]})
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        return rst

    def linkException(self, instance):
        """
        Função que valida se tem solicitação vinculada
        Args:
            employee
        Returns:
            bool:
        """
        if instance.server_duty.exists():
            raise LinkException(
                f"""Não é possível remover/editar a solicitação, 
                    pois a mesma está vinculada a solicitação nº {instance.server_duty.get().pk}.
            """
            )
        else:
            return True
