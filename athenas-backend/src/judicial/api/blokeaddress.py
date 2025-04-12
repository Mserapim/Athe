# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import BlokeAddress
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudBlokeAddress(Restful):

    _model = BlokeAddress

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "location" in params:
            if params.get("location") != "":
                field = getattr(self.Model, "location")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(location=query.get(pk=params.get("location")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(location=None)

        if "bloke" in params:
            if params.get("bloke") != "":
                field = getattr(self.Model, "bloke")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(bloke=query.get(pk=params.get("bloke")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(bloke=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            location=nil_pk(instance.location, None),
            location_unicode=nil_unicode(instance.location, None),
            district=instance.district,
            address=instance.address,
            bloke=nil_pk(instance.bloke, None),
            bloke_unicode=nil_unicode(instance.bloke, None),
            complement=instance.complement,
            observation=instance.observation,
        )

        return rst
