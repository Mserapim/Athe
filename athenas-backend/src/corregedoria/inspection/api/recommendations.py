# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import Recommendations
import raf.api.util

log = getLogger(__name__)


class INSPECTIONRecommendations(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = Recommendations

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.recommendations.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONRecommendations, self).model_to_dict(instance)
        _dict_.update(
            {
                "deadline_grid": (
                    instance.deadline.strftime("%d/%m/%Y")
                    if instance.waiting_response and instance.deadline
                    else "--"
                ),
            }
        )
        return _dict_
