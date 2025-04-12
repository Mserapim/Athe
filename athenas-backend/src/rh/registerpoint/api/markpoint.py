# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.registerpoint.models import MarkPoint


log = getLogger(__name__)


class MarkPointAdmin(RestfulDRY):

    _model = MarkPoint

    full_text_index = ("employee__pessoa_fisica__nome__icontains", "pk__iexact")

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)

        _dict_.update(
            {
                "date": instance.get_date,
                "mark": instance.mark.strftime("%H:%M:%S"),
                "name": instance.get_name,
                "register": instance.get_register,
                "workplace": instance.get_workplace,
                "ip": instance.ip,
            }
        )

        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.registerpoint.MarkPointManage")')
