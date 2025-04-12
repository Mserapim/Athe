# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import RejectionLinkOther
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudRejectionLinkOther(BasePartLawsuit, Restful):

    _model = RejectionLinkOther

    def get_params(self, *args, **kargs):
        params = super(EJudRejectionLinkOther, self).get_params(*args, **kargs)

        if "other_lawsuit_organ" in params:
            if params.get("other_lawsuit_organ") != "":
                field = getattr(self.Model, "other_lawsuit_organ")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        other_lawsuit_organ=query.get(
                            pk=params.get("other_lawsuit_organ")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(other_lawsuit_organ=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudRejectionLinkOther, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                other_lawsuit_number=instance.other_lawsuit_number,
                other_lawsuit=instance.other_lawsuit,
                other_lawsuit_display=nil_display(instance, "other_lawsuit", None),
                despatch=instance.despatch,
                other_lawsuit_organ=nil_pk(instance.other_lawsuit_organ, None),
                other_lawsuit_organ_unicode=nil_unicode(
                    instance.other_lawsuit_organ, None
                ),
            )

        return rst
