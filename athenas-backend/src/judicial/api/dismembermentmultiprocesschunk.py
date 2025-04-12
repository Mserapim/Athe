# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import DismembermentMultiProcessChunk
from judicial.api.partlawsuit import BasePartLawsuit
from contrib.nil import nil_pk, nil_unicode

log = getLogger(__name__)


class EjudDismembermentMultiProcessChunk(Restful):

    _model = DismembermentMultiProcessChunk

    force_upper = False

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            change_title=instance.change_title,
            main_matter=nil_pk(instance.main_matter, None),
            main_matter_unicode=nil_unicode(instance.main_matter, None),
        )

        return rst

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for relname in ("dismemberment", "main_matter"):
            if relname in params:
                if params.get(relname) != "":
                    field = getattr(self.Model, relname)

                    query = field.get_queryset()

                    try:
                        params.update({relname: query.get(pk=params.get(relname))})
                    except Exception as e:
                        log.exception(e)
                        raise e
                else:
                    params.update({relname: None})

        return params
