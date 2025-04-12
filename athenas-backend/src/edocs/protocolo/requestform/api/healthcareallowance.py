# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import (
    HealthcareAllowanceForActiveEmployee,
    HealthcareAllowanceForInactiveEmployee,
)


log = getLogger(__name__)


class RFHealthcareActiveEmployee(EDOCManage):

    _model = HealthcareAllowanceForActiveEmployee

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        try:
            params.update(request_type=int(params.get("request_type", "")))
        except ValueError:
            raise Exception(
                "Por favor, preencha corretamente o campo 'Tipo de requerimento'."
            )

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        request_type = instance.protocolo.my_origin.request_type
        data.update({"request_type": request_type if request_type is not None else ""})

        return data


class RFHealthcareInactiveEmployee(EDOCManage):

    _model = HealthcareAllowanceForInactiveEmployee

    def requiredParam(self, param):
        raise Exception(f"Por favor, preencha corretamente o campo '{param}'.")

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("address", ""):
            self.requiredParam("Endereço")

        if not params.get("contact_number", ""):
            self.requiredParam("Telefone para contato")

        try:
            params.update(beneficiary_type=int(params.get("beneficiary_type", "")))
        except ValueError:
            self.requiredParam("Tipo de beneficiário")

        try:
            params.update(request_type=int(params.get("request_type", "")))
        except ValueError:
            self.requiredParam("Tipo de requerimento")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        obj = instance.protocolo.my_origin
        data.update(
            {
                "address": obj.address or "",
                "contact_number": obj.contact_number or "",
                "beneficiary_type": (
                    obj.beneficiary_type if obj.beneficiary_type is not None else ""
                ),
                "request_type": (
                    obj.request_type if obj.request_type is not None else ""
                ),
            }
        )

        return data
