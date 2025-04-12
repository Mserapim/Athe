# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import SocialProgram


class RHSocialProgramRestful(RestfulDRY):

    full_text_index = ("name__icontains",)

    exclude_fields = ["audittimestampmodel_ptr", "auditablemixins_ptr"]

    _model = SocialProgram

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.socialprogram.Manage")')
