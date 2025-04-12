# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.models import ConfigScoreTable
import raf.api.util

log = getLogger(__name__)


class CORREGEDORIAScoreTable(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = ConfigScoreTable

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.scoretable.Launcher")')
