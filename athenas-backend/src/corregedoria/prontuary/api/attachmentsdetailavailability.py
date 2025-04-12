# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import AttachmentsDetailAvailability
import raf.api.util

log = getLogger(__name__)


class PRONTUARYAttachmentsDetailAvailability(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = AttachmentsDetailAvailability

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.career.others.availability.attachments.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYAttachmentsDetailAvailability, self).model_to_dict(
            instance
        )
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
