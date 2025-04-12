# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Judicialization
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class EJudJudicialization(BasePartLawsuit, Restful):

    _model = Judicialization

    def complement_model_to_dict(self, instance):
        rst = super(EJudJudicialization, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                code=instance.code,
                court=instance.court,
                observation=instance.observation,
            )

        return rst
