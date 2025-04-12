# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import SuspendDeadline
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class EJudSuspendDeadline(BasePartLawsuit, Restful):

    _model = SuspendDeadline

    def complement_model_to_dict(self, instance):
        rst = super(EJudSuspendDeadline, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(remaining_days=instance.remaining_days)

        return rst
