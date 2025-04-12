# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import ExistingRegisters
import raf.api.util

log = getLogger(__name__)


class INSPECTIONExistingRegisters(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = ExistingRegisters

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONExistingRegisters, self).model_to_dict(instance)
        _dict_.update(
            {
                "registration_type_display": instance.get_registration_type_display(),
            }
        )
        return _dict_
