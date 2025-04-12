# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import DilationManifestation
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_pk, nil_unicode

log = getLogger(__name__)


class EJudDilationManifestation(BasePartLawsuit, Restful):

    _model = DilationManifestation

    def get_params(self, *args, **kargs):
        params = super(EJudDilationManifestation, self).get_params(*args, **kargs)

        if "manifestation" in params:
            if params.get("manifestation") != "":
                field = getattr(self.Model, "manifestation")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        manifestation=query.get(pk=params.get("manifestation"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(manifestation=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudDilationManifestation, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                manifestation=nil_pk(instance.manifestation, None),
                manifestation_unicode=nil_unicode(instance.manifestation, None),
                content=instance.content,
                dilation_days=instance.dilation_days,
            )

        return rst
