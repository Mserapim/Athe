# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.models import BandScoreTable
import raf.api.util

log = getLogger(__name__)


class CORREGEDORIABandScoreTable(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = BandScoreTable

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.scoretable.bandscoretable.Launcher")'
        )
