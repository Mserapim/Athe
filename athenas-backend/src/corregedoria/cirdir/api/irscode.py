# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import IRSCode

log = getLogger(__name__)


class CIRDIRIRSCode(RestfulDRY):

    force_upper = False

    full_text_index = ["title__icontains"]

    _model = IRSCode

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cirdir.irscode.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRIRSCode, self).model_to_dict(instance)

        return _dict_
