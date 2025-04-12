# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import PreInvestigationFact
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EjudPreInvestigationFact(BasePartLawsuit, Restful):

    _model = PreInvestigationFact

    def complement_model_to_dict(self, instance):
        rst = super(EjudPreInvestigationFact, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(justify=instance.justify)

        return rst
