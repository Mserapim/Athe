# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from common.clinical.models import Doctor


log = getLogger(__name__)


class ClinicalDoctor(RestfulDRY):

    _model = Doctor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.clinical.doctor.Manage")')
