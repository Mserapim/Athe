# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import UnConnect
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_unicode

log = getLogger(__name__)


class EJudUnConnect(BasePartLawsuit, Restful):

    _model = UnConnect

    def get_params(self, *args, **kargs):
        params = super(EJudUnConnect, self).get_params(*args, **kargs)

        if "unconnect_lawsuit" in params:
            if params.get("unconnect_lawsuit") != "":
                field = getattr(self.Model, "unconnect_lawsuit")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        unconnect_lawsuit=query.get(pk=params.get("unconnect_lawsuit"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(unconnect_lawsuit=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudUnConnect, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                unconnect_lawsuit=instance.unconnect_lawsuit.pk,
                unconnect_lawsuit_unicode=nil_unicode(instance.unconnect_lawsuit, None),
            )

        return rst
