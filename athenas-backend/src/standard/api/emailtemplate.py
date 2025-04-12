# -*- coding: utf-8 -*-
import json

from contrib.newrest import RestfulDRY, Restful
from contrib.utils import getLogger
from standard.models import EmailTemplate

log = getLogger(__name__)


class STDEmailTemplate(RestfulDRY):

    full_text_index = (
        "code__icontains",
        "subject__icontains",
        "contents__icontains",
        "description__icontains",
    )

    _model = EmailTemplate

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("standard.emailtemplate.Manage")')
