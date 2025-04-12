# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from standard.models import ConfigPoint


log = getLogger(__name__)


class STDConfigPoint(RestfulDRY):

    _model = ConfigPoint

    full_text_index = (
        "place__icontains",
        "prosecution__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("standard.configpoint.Manage")')
