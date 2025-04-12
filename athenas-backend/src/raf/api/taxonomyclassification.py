# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from raf.models import TaxonomyClassification

log = getLogger(__name__)


class RAFTaxonomyClassification(RestfulDRY):

    _model = TaxonomyClassification

    force_upper = False

    def model_to_dict(self, instance):
        _dict_ = super(RAFTaxonomyClassification, self).model_to_dict(instance)

        _dict_.update(
            {"cnmp_code": str(instance.cnmp_code), "title": str(instance.title)}
        )

        return _dict_
