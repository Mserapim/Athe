# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from contrib.newrest import RestfulDRY
from rh.api.person import RHNaturalPersonRestful


log = getLogger(__name__)


class PVFRHPersonRestful(RHNaturalPersonRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.person.Manage")')
