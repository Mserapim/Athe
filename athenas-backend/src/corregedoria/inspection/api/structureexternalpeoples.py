# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import StructureExternalPeoples
from rh.models import MovimentacaoPosse as PossessionMovement

log = getLogger(__name__)


class INSPECTIONStructureExternalPeoples(RestfulDRY):

    force_upper = True

    full_text_index = ()

    _model = StructureExternalPeoples

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONStructureExternalPeoples, self).model_to_dict(instance)
        return _dict_
