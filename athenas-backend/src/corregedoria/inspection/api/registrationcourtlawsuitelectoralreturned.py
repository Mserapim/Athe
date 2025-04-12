# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import RegistrationCourtLawsuitElectoralReturned
import raf.api.util

log = getLogger(__name__)


class INSPECTIONRegistrationCourtLawsuitElectoralReturned(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = RegistrationCourtLawsuitElectoralReturned

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.registrationcourtlawsuitelectoralreturned.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(
            INSPECTIONRegistrationCourtLawsuitElectoralReturned, self
        ).model_to_dict(instance)
        _dict_.update(
            {
                "sum_amount": instance.sum_amount,
            }
        )
        return _dict_
