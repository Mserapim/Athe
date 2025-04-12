# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Archivement
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudArchivement(BasePartLawsuit, Restful):

    _model = Archivement

    def complement_model_to_dict(self, instance):
        rst = super(EJudArchivement, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                despatch=instance.despatch,
            )

        return rst
