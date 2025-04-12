# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import ValorContrato as AgreementValue
from contrib.nil import nil_display


log = getLogger(__name__)


class PHAAgreementValue(RestfulDRY):

    _model = AgreementValue

    force_upper = False

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            ordem_display=nil_display(instance, "ordem", None),
            tipo_valor_contrato_display=nil_display(
                instance, "tipo_valor_contrato", None
            ),
        )

        return rst
