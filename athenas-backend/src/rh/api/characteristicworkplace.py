# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import CharacteristicWorkplace


class RHCharacteristicWorkplace(RestfulDRY):

    _model = CharacteristicWorkplace

    force_upper = False

    full_text_index = ("name__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.characteristicworkplace.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(RHCharacteristicWorkplace, self).model_to_dict(instance)
        return _dict_
