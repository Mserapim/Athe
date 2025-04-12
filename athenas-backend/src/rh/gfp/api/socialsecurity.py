# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import SocialSecurity, SocialSecurityRange


log = getLogger(__name__)


class GFPSocialSecurityRange(RestfulDRY):

    _model = SocialSecurityRange

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.socialsecurity.SocialSecurityRangeManage")'
        )


class GFPSocialSecurity(RestfulDRY):

    _model = SocialSecurity

    full_text_index = ("legal_person__nome__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.socialsecurity.SocialSecurityManage")')
