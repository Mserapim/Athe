# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import PrivateLog

log = getLogger(__name__)


class CIRDIRPrivateLog(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = PrivateLog

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cirdir.provatelog.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRPrivateLog, self).model_to_dict(instance)
        _dict_.update({"create": instance.created_at.strftime("%d/%m/%Y %H:%M:%S")})
        return _dict_
