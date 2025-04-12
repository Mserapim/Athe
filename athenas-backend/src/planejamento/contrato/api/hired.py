# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import Hired
from contrib.nil import nil_display


log = getLogger(__name__)


class PHAHired(RestfulDRY):

    _model = Hired

    force_orm_single = True

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        return rst
