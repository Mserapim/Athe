# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import Discipline

log = getLogger(__name__)


class CIRDIRDiscipline(RestfulDRY):

    force_upper = False

    full_text_index = [
        "name__icontains",
    ]

    _model = Discipline

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.teaching.discipline.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRDiscipline, self).model_to_dict(instance)
        _dict_.update({})
        return _dict_
