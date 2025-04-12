# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.ferias.models import Configuracao

log = getLogger(__name__)


class FRSConfiguration(RestfulDRY):

    _model = Configuracao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.configuration.Manage")')
