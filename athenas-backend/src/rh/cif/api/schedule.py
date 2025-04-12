# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_new_display, nil_pk
from contrib.utils import getLogger
from rh.cif.models import Schedule

log = getLogger(__name__)


class CifSchedule(Restful):

    _model = Schedule

    full_text_index = (
        "start_time__icontains",
        "end_time__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.schedule.Manage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)
        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            day_week=str(instance.day_week),
            day_week_display=nil_new_display(instance, "day_week", ""),
            start_time=str(instance.start_time) or None,
            end_time=str(instance.end_time) or None,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
        )

        return rst
