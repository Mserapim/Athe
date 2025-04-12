from rh.pvf.models import PortalRetificationSchedule
from rest_framework.serializers import ModelSerializer
from contrib.utils import getLogger
from rh.pvf.apiv2.utils.retification import extract_selections_usufructs
from rh.pvf.apiv2.utils.base import formart_date_str
import json


log = getLogger(__name__)


class PVFRetificationScheduleSerializers(ModelSerializer):

    class Meta:
        model = PortalRetificationSchedule
        fields = []

    def extract_params(self, params, signature=[]):
        params_new = {}
        for key in signature:
            if key in params:
                try:
                    params_new.update(
                        {key: json.loads(params[key]) if params[key] != "" else None}
                    )
                    for values in params_new[key]:
                        values["start_date"] = formart_date_str(values["start_date"])
                        values["end_date"] = formart_date_str(values["end_date"])

                except:
                    params_new.update({key: params[key]})
                    for values in params_new[key]:
                        values["start_date"] = formart_date_str(values["start_date"])
                        values["end_date"] = formart_date_str(values["end_date"])
        return params_new

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            modifieds, all_modifieds, total_days, days_usufructs = (
                extract_selections_usufructs(data.get("usufructs_ids"))
            )
            params.update(
                {
                    "usufructs_in": self.extract_params(data, ["usufructs_in"]),
                    "observation": data.get("observation"),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "parcel_number": data.get("parcel_number"),
                    "modifieds": modifieds,
                    "all_modifieds": all_modifieds,
                    "total_days": total_days,
                    "days_usufructs": days_usufructs,
                }
            )
            instance = self.Meta.model.create_request_retification(params)
            rst.update(
                {
                    "success": True,
                    "message": "Registro criado com sucesso",
                    "data": {
                        "pk": instance.pk,
                        "type_of_request": instance.type_of_request,
                        "date": instance.date,
                        "employee_name": instance.employee_name,
                        "approver": instance.set_custom_approver,
                        "status_name": instance.status_name,
                        "acquisitive_period": instance.acquisitive_period,
                    },
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst
