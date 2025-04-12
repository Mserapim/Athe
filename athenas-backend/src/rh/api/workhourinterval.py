# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import WorkHourInterval

log = getLogger(__name__)


class RHWorkHourInterval(RestfulDRY):

    _model = WorkHourInterval

    full_text_index = (
        "title__icontains",
        "code__icontains",
        "duration_hour__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.workhourinterval.Manage")')

    def model_to_dict(self, instance):
        params = super(RHWorkHourInterval, self).model_to_dict(instance)
        params.update(
            {
                "time_start_formated": instance.time_start_formated,
                "time_end_formated": instance.time_end_formated,
            }
        )
        return params
