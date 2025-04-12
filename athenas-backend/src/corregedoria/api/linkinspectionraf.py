# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.models import ConfigLinkInspectionRAF
import raf.api.util

log = getLogger(__name__)


class CORREGEDORIALinkInspectionRAF(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = ConfigLinkInspectionRAF

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.linkinspectionraf.Launcher")')

    def model_to_dict(self, instance):
        _dict_ = super(CORREGEDORIALinkInspectionRAF, self).model_to_dict(instance)
        _dict_.update(
            {
                "raf_quiz": instance.raf_subitem.quiz.typequiz.title,
            }
        )
        return _dict_
