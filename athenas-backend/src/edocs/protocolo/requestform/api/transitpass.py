# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import TransitPass
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormTransitPass(EDOCManage):

    _model = TransitPass

    def prepare_params(self, querydict):
        params = super(RequestFormTransitPass, self).prepare_params(querydict)

        try:
            params.update(request_type=int(params.get("request_type", "")))
        except ValueError:
            raise Exception(
                "Por favor, preencha corretamente o campo Tipo requerimento."
            )

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormTransitPass, self).model_to_dict(instance)

        form = instance.protocolo.transitpass

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                ),
                "request_type": (
                    form.request_type if form.request_type is not None else ""
                ),
            }
        )

        return data
