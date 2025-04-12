# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import AdditionalDiligence
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class EjudAdditionalDiligence(BasePartLawsuit, Restful):

    _model = AdditionalDiligence

    def complement_model_to_dict(self, instance):
        rst = super(EjudAdditionalDiligence, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                justification=instance.justification,
                dispatch_title=instance.dispatch_title,
            )

        return rst
