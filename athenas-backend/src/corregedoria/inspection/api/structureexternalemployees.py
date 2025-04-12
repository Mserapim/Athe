# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import StructureExternalEmployees
from rh.models import MovimentacaoPosse as PossessionMovement

from corregedoria.utils import format_category_employee

log = getLogger(__name__)


class INSPECTIONStructureExternalEmployees(RestfulDRY):

    force_upper = True

    full_text_index = ()

    _model = StructureExternalEmployees

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONStructureExternalEmployees, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "see_employee_unicode": instance.external_employee.servidor.pessoa_fisica.nome,
                "see_occupation_unicode": (
                    instance.external_employee.movimentacaoposse.quadro.cargo.nome
                    if PossessionMovement.objects.filter(
                        pk=instance.external_employee.pk
                    ).exists()
                    else None
                ),
                "see_category": format_category_employee(
                    instance.external_employee.servidor.categoria_cache
                ),
            }
        )
        return _dict_
