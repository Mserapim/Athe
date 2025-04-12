# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import EmployeeRequest
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormEmployee(EDOCManage):

    _model = EmployeeRequest

    def prepare_params(self, querydict):
        params = super(RequestFormEmployee, self).prepare_params(querydict)

        try:
            params.update(request_type=int(params.get("request_type", "")))
        except ValueError:
            raise Exception("Por favor, preencha corretamente o campo Requerimento.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormEmployee, self).model_to_dict(instance)
        request_type = instance.protocolo.my_origin.request_type
        data.update(
            {
                "request_type": (
                    request_type if request_type is not None else "Não informado"
                )
            }
        )
        return data
