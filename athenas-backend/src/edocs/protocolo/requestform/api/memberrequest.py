# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import MemberRequest
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormMember(EDOCManage):

    _model = MemberRequest

    def prepare_params(self, querydict):
        params = super(RequestFormMember, self).prepare_params(querydict)

        try:
            params.update(request_type=int(params.get("request_type", "")))
        except ValueError:
            raise Exception("Por favor, preencha corretamente o campo Requerimento.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormMember, self).model_to_dict(instance)
        request_type = instance.protocolo.my_origin.request_type
        data.update(
            {
                "request_type": (
                    request_type if request_type is not None else "Não informado"
                )
            }
        )
        return data
