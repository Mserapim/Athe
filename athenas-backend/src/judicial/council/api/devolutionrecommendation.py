# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import DevolutionRecommendation
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class CouncilDevolutionRecommendation(BasePartLawsuit, Restful):

    _model = DevolutionRecommendation

    def get_params(self, *args, **kargs):
        params = super(CouncilDevolutionRecommendation, self).get_params(*args, **kargs)

        if "devolution_to" in params:
            if params.get("devolution_to") != "":
                field = getattr(self.Model, "devolution_to")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        devolution_to=query.get(pk=params.get("devolution_to"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(devolution_to=None)

        return params

    def model_to_dict(self, instance):
        rst = super(CouncilDevolutionRecommendation, self).model_to_dict(instance)

        rst.update(
            justification=instance.justification,
            devolution_to=nil_pk(instance.devolution_to, None),
            devolution_to_unicode=nil_unicode(instance.devolution_to, None),
        )

        return rst
