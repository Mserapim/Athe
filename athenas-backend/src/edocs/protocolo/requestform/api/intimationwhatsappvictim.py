# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import (
    IntimationWhatsAppAuthenticityVerifiableVictim,
)

log = getLogger(__name__)


class RequestIntimationWhatsAppVictim(EDOCManage):
    _model = IntimationWhatsAppAuthenticityVerifiableVictim

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        # if not params.get('name_intimate', ''):
        #     raise Exception('Por favor, preencha corretamente o NOME do indiciado.')

        # if not params.get('cpf_intimate', ''):
        #     raise Exception('Por favor, preencha corretamente o CPF do indiciado.')

        if not params.get("name_victim", ""):
            raise Exception("Por favor, preencha corretamente o NOME da vítima.")

        if not params.get("cpf_victim", ""):
            raise Exception("Por favor, preencha corretamente o CPF da vítima.")

        if not params.get("number_inquiry_police", ""):
            raise Exception(
                "Por favor, preencha corretamente o Nº DO INQUÉRITO POLICIAL"
            )

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        report = instance.protocolo.intimationwhatsappauthenticityverifiablevictim

        data.update(
            {
                "name_intimate": (
                    report.name_intimate if report.name_intimate is not None else ""
                ),
                "cpf_intimate": report.cpf_intimate or "",
                "name_victim": (
                    report.name_victim if report.name_victim is not None else ""
                ),
                "cpf_victim": report.cpf_victim or "",
                "number_inquiry_police": (
                    report.number_inquiry_police
                    if report.number_inquiry_police is not None
                    else ""
                ),
            }
        )

        return data
