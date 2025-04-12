# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from workflow.models import Vertex


log = getLogger(__name__)


class WFLWVertexRestful(RestfulDRY):

    full_text_index = (
        "acronym__icontains",
        "kind__icontains",
        "vertices__name__icontains",
        "vertices__acronym__icontains",
    )

    _model = Vertex

    force_upper = False

    exclude_fields = ["common_ptr"]

    force_persist_boolean_fields = ["active", "beginning"]

    def get_icons(self, instance):

        vertex_map = {
            "workflow.models.LotacaoVertex": {
                "iconCls": "icon-wf icon-workplacevertex",
                "title": "Lotação",
            },
            "workflow.models.ServidorVertex": {
                "iconCls": "icon-wf icon-employeevertex",
                "title": "Servidor",
            },
            "workflow.models.PessoaVertex": {
                "iconCls": "icon-wf icon-personvertex",
                "title": "Pessoa",
            },
            "workflow.models.JokerVertex": {
                "iconCls": "icon-wf icon-jokervertex",
                "title": "Coringa",
            },
        }

        return vertex_map.get(instance.kind)

    def model_to_dict(self, instance):
        _dict_ = super(WFLWVertexRestful, self).model_to_dict(instance)

        _dict_.update(
            {
                "icons": self.get_icons(instance),
            }
        )

        return _dict_
