# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import BookOfRegisterOutCourtLawsuitControl
import raf.api.util

log = getLogger(__name__)


class INSPECTIONBookOfRegisterOutCourtLawsuitControl(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = BookOfRegisterOutCourtLawsuitControl

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.bookofregisteroutcourtlawsuitcontrol.Launcher")'
        )
