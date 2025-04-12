# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import MobileLiabilityStatement
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormMobileLiabilityStatement(EDOCManage):

    _model = MobileLiabilityStatement

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("imei", ""):
            raise Exception("Por favor, preencha corretamente o campo IMEI.")

        if not params.get("phone_number", ""):
            raise Exception("Por favor, preencha corretamente o campo Nº da linha.")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        form = instance.protocolo.mobileliabilitystatement

        data.update(
            {
                "imei": form.imei,
                "phone_number": form.phone_number,
                "phone_description": form.phone_description,
            }
        )

        return data
