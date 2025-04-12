# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import AttachmentsDetailTrainingImprovement
import raf.api.util

log = getLogger(__name__)


class PRONTUARYAttachmentsDetailTrainingImprovement(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = AttachmentsDetailTrainingImprovement

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.individualperformance.trainingimprovement.attachments.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(
            PRONTUARYAttachmentsDetailTrainingImprovement, self
        ).model_to_dict(instance)
        _dict_.update(
            {
                "attached_file_url": (
                    instance.attached_file.complete_permalink()
                    if hasattr(instance, "attach")
                    else None
                ),
            }
        )
        return _dict_
