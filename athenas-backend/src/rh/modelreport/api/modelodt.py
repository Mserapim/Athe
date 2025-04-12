# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.modelreport.models import ModelODT


log = getLogger(__name__)


class ModelReportODT(RestfulDRY):

    _model = ModelODT

    full_text_index = ("name__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.modelreport.odt.Manage")')
