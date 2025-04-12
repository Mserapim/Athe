# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import AttachmentsDetailPromotion
import raf.api.util

log = getLogger(__name__)


class PRONTUARYAttachmentsDetailPromotion(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = AttachmentsDetailPromotion

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.career.movement.promotion.attachments.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYAttachmentsDetailPromotion, self).model_to_dict(
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
