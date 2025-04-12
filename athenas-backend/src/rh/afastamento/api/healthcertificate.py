# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.afastamento.models import HealthCertificate


class AFAHealthCertificate(RestfulDRY):

    _model = HealthCertificate

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.healthcertificate.Manage")')
