# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import ThirteenthAnticipation
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormThirteenthAnticipation(EDOCManage):

    _model = ThirteenthAnticipation

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        try:
            params.update(option_term=int(params.get("option_term", "")))
        except ValueError:
            raise Exception("Por favor, preencha corretamente o campo Termo de opção.")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        form = instance.protocolo.thirteenthanticipation

        data.update(
            {
                "contact_number": form.contact_number or "",
                "option_term": form.option_term if form.option_term is not None else "",
            }
        )

        return data
