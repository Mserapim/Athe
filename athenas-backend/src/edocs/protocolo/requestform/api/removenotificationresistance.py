# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.api.manage import EDOCManage
from edocs.protocolo.requestform.models import RemoveNotificationResistance

log = getLogger(__name__)


class RFRemoveNotificationResistance(EDOCManage):

    _model = RemoveNotificationResistance

    def prepare_params(self, querydict):
        params = super().prepare_params(querydict)

        if not params.get("cancellation_vacancies", False):
            raise Exception("Por favor preencha o campo Vagas de desistência")

        # if not params.get('resistance_declaration', False):
        #     raise Exception('Por favor preencha o campo Declaração de desistência')

        return params

    def model_to_dict(self, instance):
        data = super().model_to_dict(instance)

        data.update(
            {
                "cancellation_vacancies": instance.protocolo.my_origin.cancellation_vacancies
                or "",
                # 'resistance_declaration': instance.protocolo.my_origin.resistance_declaration or '',
            }
        )

        return data
