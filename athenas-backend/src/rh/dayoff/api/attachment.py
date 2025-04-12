# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.dayoff.models import Attachment


log = getLogger(__name__)


class DAYOFFAttachment(RestfulDRY):

    _model = Attachment

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.attachment.Manage")')
