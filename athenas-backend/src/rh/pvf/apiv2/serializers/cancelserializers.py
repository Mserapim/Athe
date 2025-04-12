import json
from rh.pvf.apiv2.utils.telework import (
    get_request_progress_telework,
    solicitacao_cancelamento_andamento,
)
from rh.pvf.models import PVFCancelamentoTeletrabalho, PortalCancelSchedule
from rest_framework.serializers import ModelSerializer
from contrib.utils import getLogger
from rh.dayoff.models import Usufruct
from rh.pvf.models import PortalRequest
from rh.pvf.const import STS_CANCELED_APPLICANT
from rh.pvf.utils.justificativas_portal_request import cancelar_justificativas_request


log = getLogger(__name__)


class PVFCancelScheduleSerializers(ModelSerializer):

    class Meta:
        model = PortalCancelSchedule
        fields = []

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            params.update(
                {
                    "usufruct_id": data.get("usufruct_id", None),
                    "observation": data.get("observation", None),
                }
            )
            instance = self.Meta.model.create_cancel_schedule(params)
            rst.update(
                {
                    "success": True,
                    "message": "Registro criado com sucesso",
                    "data": {
                        "pk": instance.pk,
                        "type_of_request": instance.type_of_request,
                        "employee_name": instance.employee_name,
                        "approver": instance.set_custom_approver,
                        "status_name": instance.status_name,
                    },
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class PVFRequestCancelSerializer(ModelSerializer):
    """
    classe serializer reponsável por realizar o cancelamento da solicitação
    """

    class Meta:
        model = PortalRequest
        fields = []

    def cancel(self, request):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            request.cancel(status=STS_CANCELED_APPLICANT)

            rst.update(success=True, message="Procedimento realizado com sucesso.")

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class PVFCancelUsufructSerializer(ModelSerializer):
    """ "
    classe serializer dos usufrutos que podem ser cancelados e retificados
    """

    class Meta:
        model = Usufruct
        fields = [
            "pk",
            "start_date",
            "end_date",
            "days",
            "type_activity",
            "start_date_acquisition",
            "type_usufruct",
            "type_usufruct_name",
        ]


class PVFCancelamentoTeletrabalhoSerializer(ModelSerializer):

    class Meta:
        model = PVFCancelamentoTeletrabalho
        fields = []

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            if (
                not get_request_progress_telework()
                and not solicitacao_cancelamento_andamento()
            ):
                params.update(
                    {
                        "request_ids": json.dumps(data.get("request_ids", None)),
                        "observation": data.get("observation", None),
                    }
                )
                instance = self.Meta.model.create(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro criado com sucesso",
                        "data": {
                            "pk": instance.pk,
                            "type_of_request": instance.type_of_request,
                            "employee_name": instance.employee_name,
                            "approver": instance.set_custom_approver,
                            "status_name": instance.status_name,
                        },
                    }
                )
            else:
                rst.update(
                    message="Já existe uma solicitação teletrabalho/cancelamento em andamento."
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst
