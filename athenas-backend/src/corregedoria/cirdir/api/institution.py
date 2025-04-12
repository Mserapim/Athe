# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.nil import nil_pk, nil_unicode
from contrib.utils import getLogger
from corregedoria.cirdir.models import Institution

log = getLogger(__name__)


class CIRDIRInstitution(RestfulDRY):

    force_upper = False

    full_text_index = [
        "razao_social__icontains",
        "nome__icontains",
        "cnpj__icontains",
    ]

    _model = Institution

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.teaching.institution.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRInstitution, self).model_to_dict(instance)
        _dict_.update(
            {
                "razao_social": instance.institution.razao_social,
                "county_unicode": nil_unicode(instance.county, None),
            }
        )
        return _dict_
