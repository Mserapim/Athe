# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import ActingZone


log = getLogger(__name__)


class EJudActingZone(Restful):

    _model = ActingZone

    full_text_index = ("title__icontains",)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.params.ActingZoneManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "enabled" in params:
            params.update(enabled=params.get("enabled", "off").lower() == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(title=instance.title, enabled=instance.enabled)

        return rst
