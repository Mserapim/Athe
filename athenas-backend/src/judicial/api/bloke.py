# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Bloke
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudBloke(Restful):

    _model = Bloke

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "lawsuit" in params:
            if params.get("lawsuit") != "":
                field = getattr(self.Model, "lawsuit")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(lawsuit=query.get(pk=params.get("lawsuit")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(lawsuit=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            my_type=instance.my_type,
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            bloke=nil_pk(instance.my_bloke, None),
            bloke_unicode=nil_unicode(instance.my_bloke, None),
        )

        return rst
