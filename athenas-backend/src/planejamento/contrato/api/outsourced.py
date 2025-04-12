# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import Outsourced


log = getLogger(__name__)


class PHAOutsourced(RestfulDRY):

    _model = Outsourced

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("planning.agreement.outsourced.Manage")')
