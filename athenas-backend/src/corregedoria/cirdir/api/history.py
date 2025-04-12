# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import History
from rh.models import Servidor

log = getLogger(__name__)


class CIRDIRHistory(RestfulDRY):

    force_upper = False

    full_text_index = [
        "action__icontains",
        "created_by__username__icontains",
        "created_by__servidor__pessoa_fisica__nome__icontains",
    ]

    _model = History

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cirdir.history.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRHistory, self).model_to_dict(instance)
        _dict_.update(
            {
                "action": instance.action,
                "dt_action": instance.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                "employee_unicode": str(instance.created_by.servidor),
            }
        )
        return _dict_
