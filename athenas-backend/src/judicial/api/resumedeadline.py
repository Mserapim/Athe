# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import ResumeDeadline
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_pk

log = getLogger(__name__)


class EJudResumeDeadline(BasePartLawsuit, Restful):

    _model = ResumeDeadline

    def complement_model_to_dict(self, instance):
        rst = super(EJudResumeDeadline, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(suspend_deadline=nil_pk(instance.suspend_deadline, None))

        return rst
