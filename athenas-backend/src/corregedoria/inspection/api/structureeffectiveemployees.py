# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import StructureEffectiveEmployees
import raf.api.util

log = getLogger(__name__)


class INSPECTIONStructureEffectiveEmployees(RestfulDRY):

    force_upper = True

    full_text_index = ()

    _model = StructureEffectiveEmployees

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONStructureEffectiveEmployees, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "sef_employee_unicode": instance.effective_employee.servidor.pessoa_fisica.nome,
                "sef_occupation_unicode": instance.effective_employee.movimentacaoposse.quadro.cargo.nome,
            }
        )
        return _dict_
