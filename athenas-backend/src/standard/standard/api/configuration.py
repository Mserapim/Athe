# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from standard.models import Configuration, Item


log = getLogger(__name__)


class STDConfiguration(RestfulDRY):

    _model = Configuration

    force_upper = False

    full_text_index = (
        "application__icontains",
        "",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("standard.configuration.Manage")')


class STDItem(RestfulDRY):

    _model = Item

    force_upper = False

    full_text_index = (
        "configuration__application__icontains",
        "key__icontains",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("standard.configuration.item.Manage")')
