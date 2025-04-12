# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import ConnectionLawsuit
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudConnectionLawsuit(BasePartLawsuit, Restful):

    _model = ConnectionLawsuit

    def get_params(self, *args, **kargs):
        params = super(EJudConnectionLawsuit, self).get_params(*args, **kargs)

        if "lawsuit_connected" in params:
            if params.get("lawsuit_connected") != "":
                field = getattr(self.Model, "lawsuit_connected")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        lawsuit_connected=query.get(pk=params.get("lawsuit_connected"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(lawsuit_connected=None)

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudConnectionLawsuit, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                text=instance.text,
                lawsuit_connected_icons=(
                    instance.lawsuit_connected.icons
                    if instance.lawsuit_connected
                    else []
                ),
                lawsuit_connected=nil_pk(instance.lawsuit_connected, None),
                lawsuit_connected_unicode=nil_unicode(instance.lawsuit_connected, None),
            )

        return rst
