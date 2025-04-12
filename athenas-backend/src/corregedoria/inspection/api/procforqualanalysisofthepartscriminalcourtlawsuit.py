# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import (
    ProcForQualAnalysisOfThePartsCriminalCourtLawsuit,
)
import raf.api.util

log = getLogger(__name__)


class INSPECTIONProcForQualAnalysisOfThePartsCriminalCourtLawsuit(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = ProcForQualAnalysisOfThePartsCriminalCourtLawsuit

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartscriminalcourtlawsuit.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(
            INSPECTIONProcForQualAnalysisOfThePartsCriminalCourtLawsuit, self
        ).model_to_dict(instance)
        _dict_.update(
            {
                "action_type_title": (
                    instance.action_type.title if instance.action_type else None
                ),
                "part_type_title": (
                    instance.part_type.title if instance.part_type else None
                ),
            }
        )
        return _dict_
