# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Dispatch
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class EJudDispatch(BasePartLawsuit, Restful):

    _model = Dispatch

    def complement_model_to_dict(self, instance):
        rst = super(EJudDispatch, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(content=instance.content, dispatch_title=instance.dispatch_title)

        return rst
