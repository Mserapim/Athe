# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.cif.models import Attachment

log = getLogger(__name__)


class CifAttachment(RestfulDRY):

    _model = Attachment

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.attachment.Manage")')
