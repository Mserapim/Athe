# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.dayoff.models import AcquisitionPeriodAttachment

log = getLogger(__name__)


class DAYOFFAcquisitionPeriodAttachmentMPMT(RestfulDRY):

    _model = AcquisitionPeriodAttachment

    full_text_index = ()

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.mpmt.acquisitionperiod.attachment.Manage")'
        )
