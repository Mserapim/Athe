# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import (
    IntimationWhatsAppAuthenticityVerifiableIntimate,
)

log = getLogger(__name__)


class RequestIntimationWhatsAppIntimate(EDOCManage):
    _model = IntimationWhatsAppAuthenticityVerifiableIntimate

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("name_intimate", ""):
            raise Exception("Por favor, preencha corretamente o NOME do indiciado.")

        if not params.get("cpf_intimate", ""):
            raise Exception("Por favor, preencha corretamente o CPF do indiciado.")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        report = instance.protocolo.intimationwhatsappauthenticityverifiableintimate

        data.update(
            {
                "name_intimate": (
                    report.name_intimate if report.name_intimate is not None else ""
                ),
                "cpf_intimate": report.cpf_intimate or "",
                "number_inquiry_police": (
                    report.number_inquiry_police
                    if report.number_inquiry_police is not None
                    else ""
                ),
            }
        )

        return data
