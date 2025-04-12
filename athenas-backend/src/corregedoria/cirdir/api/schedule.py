# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import Schedule

log = getLogger(__name__)


class CIRDIRSchedule(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = Schedule

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.teaching.schedule.Manage")'
        )

    def get_query(self, args=[]):
        query = super(CIRDIRSchedule, self).get_query()
        return query.order_by("day_week", "start_time")

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRSchedule, self).model_to_dict(instance)
        _dict_.update(
            {
                "unicode": str(instance),
            }
        )
        return _dict_
