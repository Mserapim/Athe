# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import LegalGround


log = getLogger(__name__)


class EJudLegalGround(Restful):

    _model = LegalGround

    full_text_index = ("title__icontains",)

    force_upper = False

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(text=instance.text, title=instance.title)

        return rst
