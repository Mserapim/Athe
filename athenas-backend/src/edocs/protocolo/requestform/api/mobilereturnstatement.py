# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import MobileReturnStatement
from edocs.protocolo.api.manage import EDOCManage
from rh.models import Servidor as Employee


log = getLogger(__name__)


class RequestFormMobileReturnStatement(EDOCManage):

    _model = MobileReturnStatement

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("imei", ""):
            raise Exception("Por favor, preencha corretamente o campo 'IMEI'.")

        if not params.get("phone_number", ""):
            raise Exception("Por favor, preencha corretamente o campo 'Nº da linha'.")

        if not params.get("phone_description", ""):
            raise Exception("Por favor, preencha corretamente o campo 'Modelo'.")

        try:
            params.update(successor=Employee.objects.get(pk=params.get("successor")))
        except Exception:
            raise Exception("Por favor, preencha corretamente o campo 'Servidor'.")

        params.update(
            returned_battery_charger=params.get("returned_battery_charger", "off")
            == "on"
        )
        params.update(
            returned_headphone=params.get("returned_headphone", "off") == "on"
        )
        params.update(
            returned_sim_ejector=params.get("returned_sim_ejector", "off") == "on"
        )

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        form = instance.protocolo.mobilereturnstatement

        data.update(
            {
                "imei": form.imei or "",
                "phone_number": form.phone_number or "",
                "phone_description": form.phone_description or "",
                "successor": form.successor.pk if form.successor else 0,
                "returned_battery_charger": form.returned_battery_charger,
                "returned_headphone": form.returned_headphone,
                "returned_sim_ejector": form.returned_sim_ejector,
            }
        )

        return data
