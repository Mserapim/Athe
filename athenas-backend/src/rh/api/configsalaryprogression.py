# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from rh.gfp.models import ConfigSalaryProgression


class RHConfigSalaryProgression(RestfulDRY):

    force_upper = False

    _model = ConfigSalaryProgression

    full_text_index = ("slug__icontains",)

    exclude_fields = [
        "audittimestampmodel_ptr",
        "auditablemixins_ptr",
    ]

    force_persist_boolean_fields = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.configsalaryprogression.Manage")')
