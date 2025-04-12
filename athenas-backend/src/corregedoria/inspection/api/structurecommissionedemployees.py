# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import StructureCommissionedEmployees
import raf.api.util

log = getLogger(__name__)


class INSPECTIONStructureCommissionedEmployees(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = StructureCommissionedEmployees

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONStructureCommissionedEmployees, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "sce_employee_unicode": instance.commissioned_employee.servidor.pessoa_fisica.nome,
                "sce_occupation_unicode": (
                    instance.commissioned_employee.movimentacaoposse.quadro.cargo.nome
                    if instance.commissioned_employee.movimentacaoposse.quadro
                    else instance.commissioned_employee.movimentacaoposse.description_possession
                ),
            }
        )
        return _dict_
