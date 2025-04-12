# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import CourtLawsuitControl
import raf.api.util

log = getLogger(__name__)


class INSPECTIONCourtLawsuitControl(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = CourtLawsuitControl

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.courtlawsuitcontrol.Launcher")'
        )
