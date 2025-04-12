# -*- coding: utf-8 -*-

from contrib.utils import DateUtils, getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import RemoveNotificationApplication

log = getLogger(__name__)


class RFRemoveNotificationApplication(EDOCManage):

    _model = RemoveNotificationApplication

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("position_start_concurso", False):
            raise Exception(
                "Por favor preencha o campo Posição no concurso de ingresso"
            )

        if not params.get("option_interest", False):
            raise Exception("Por favor preencha o campo Vagas de interesse")

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        data.update(
            {
                "position_start_concurso": instance.protocolo.my_origin.position_start_concurso
                or "",
                "option_interest": instance.protocolo.my_origin.option_interest or "",
            }
        )

        return data
