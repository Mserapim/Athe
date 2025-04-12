# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import DearchivingDispatch
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_display

log = getLogger(__name__)


class EJudDearchivingDispatch(BasePartLawsuit, Restful):

    _model = DearchivingDispatch

    def get_params(self, *args, **kargs):
        params = super(EJudDearchivingDispatch, self).get_params(*args, **kargs)

        if "dearchiving_type" in params:
            if params.get("dearchiving_type") == "":
                params.pop("dearchiving_type")

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudDearchivingDispatch, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                dearchiving_type=instance.dearchiving_type,
                dearchiving_type_display=nil_display(
                    instance, "dearchiving_type", None
                ),
                content=instance.content,
            )

        return rst
