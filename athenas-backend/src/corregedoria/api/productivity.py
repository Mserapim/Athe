# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.models import ConfigProductivity
import raf.api.util

log = getLogger(__name__)


class CORREGEDORIAProductivity(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = ConfigProductivity

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.productivity.bandscoretable.Launcher")'
        )
