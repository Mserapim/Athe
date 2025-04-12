# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import SupplementOrdinace
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudSupplementOrdinace(BasePartLawsuit, Restful):

    _model = SupplementOrdinace

    def get_params(self, *args, **kargs):
        params = super(EJudSupplementOrdinace, self).get_params(*args, **kargs)

        if "ordinace" in params:
            if params.get("ordinace") != "":
                field = getattr(self.Model, "ordinace")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(ordinace=query.get(pk=params.get("ordinace")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(ordinace=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudSupplementOrdinace, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                justification=instance.justification,
                ordinace=nil_pk(instance.ordinace, None),
                ordinace_unicode=nil_unicode(instance.ordinace, None),
            )

        return rst
