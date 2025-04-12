# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.nil import nil_unicode, nil_pk
from raf.models import SpecialOrgan

log = getLogger(__name__)


class RAFSpecialOrgan(RestfulDRY):

    force_upper = False

    _model = SpecialOrgan

    full_text_index = (
        "location__nome__icontains",
        "location__sigla__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = super(RAFSpecialOrgan, self).model_to_dict(instance)

        _dict_.update(
            {
                "location_unicode": nil_unicode(instance.location, None),
                "location": nil_pk(instance.location, None),
            }
        )

        return _dict_
