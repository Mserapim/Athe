# -*- coding: utf-8 -*-
from judicial.api.legalclassification import EJudLegalClassification
from contrib.utils import getLogger
from judicial.models import LegalClass
from contrib.nil import nil_display


log = getLogger(__name__)


class EJudLegalClass(EJudLegalClassification):

    _model = LegalClass

    def get_params(self, *args, **kwags):
        params = super(EJudLegalClass, self).get_params(*args, **kwags)

        if "instauration" in params and params.get("instauration") == "":
            params.update(instauration=None)

        return params

    def model_to_dict(self, inst):
        _dict = super(EJudLegalClass, self).model_to_dict(inst)

        _dict.update(
            instauration=inst.instauration,
            instauration_display=nil_display(inst, "instauration", None),
        )

        return _dict
