# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.dayoff.models import AcquisitionPeriodAttachment

log = getLogger(__name__)


class DAYOFFAcquisitionPeriodAttachment(RestfulDRY):

    _model = AcquisitionPeriodAttachment

    full_text_index = ()

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.acquisitionperiod.attachment.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(DAYOFFAcquisitionPeriodAttachment, self).model_to_dict(instance)
        _dict_.update({"status": 1 if instance.status is None else instance.status})
        return _dict_
