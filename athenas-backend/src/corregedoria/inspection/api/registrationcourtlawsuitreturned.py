# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import RegistrationCourtLawsuitReturned
import raf.api.util

log = getLogger(__name__)


class INSPECTIONRegistrationCourtLawsuitReturned(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = RegistrationCourtLawsuitReturned

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.registrationcourtlawsuitreturned.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONRegistrationCourtLawsuitReturned, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "sum_amount": instance.sum_amount,
            }
        )
        return _dict_
