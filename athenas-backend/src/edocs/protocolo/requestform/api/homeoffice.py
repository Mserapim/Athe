# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import HomeOfficeForEmployee


log = getLogger(__name__)


class RFHomeOfficeForEmployee(EDOCManage):

    _model = HomeOfficeForEmployee

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        try:
            params.update(request_type=int(params.get("request_type", "")))
        except ValueError:
            raise Exception(
                "Por favor, preencha corretamente o campo 'Condição do Servidor'."
            )

        if not params.get("justification", False):
            raise Exception("Por favor preencha o campo Justificativa")

        if not params.get("schedule", False):
            raise Exception("Por favor preencha o campo Cronograma")

        if not params.get("activities_goals", False):
            raise Exception("Por favor preencha o campo Atividades e Metas")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        request_type = instance.protocolo.my_origin.request_type
        data.update(
            {
                "request_type": request_type if request_type is not None else "",
                "justification": instance.protocolo.my_origin.justification or "",
                "activities_goals": instance.protocolo.my_origin.activities_goals or "",
                "schedule": instance.protocolo.my_origin.schedule or "",
            }
        )

        return data
