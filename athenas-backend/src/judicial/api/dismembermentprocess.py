# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import DismembermentProcess
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class EjudDismembermentProcess(BasePartLawsuit, Restful):

    _model = DismembermentProcess

    def complement_model_to_dict(self, instance):
        rst = super(EjudDismembermentProcess, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                change_title=instance.change_title, justification=instance.justification
            )

        return rst
