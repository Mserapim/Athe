# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import ProfissionalSaude

log = getLogger(__name__)


class RHProfissionalSaudeRestful(RestfulDRY):

    _model = ProfissionalSaude

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.profissionalsaude.Manage")')
