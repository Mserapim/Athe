# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import PublicConcurrence


class RHPublicConcurrenceRestful(RestfulDRY):

    _model = PublicConcurrence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.publicconcurrence.Manage")')
