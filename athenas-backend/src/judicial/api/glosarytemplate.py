# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import GlosaryTemplate
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EJudGlosaryTemplate(Restful):

    _model = GlosaryTemplate

    force_upper = False

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "glosary" in params:
            if params.get("glosary") != "":
                field = getattr(self.Model, "glosary")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(glosary=query.get(pk=params.get("glosary")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(glosary=None)

        if "active" in params:
            params.update(active=params.get("active") == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            template=instance.template,
            title=instance.title,
            active=instance.active,
            glosary=nil_pk(instance.glosary, None),
            glosary_unicode=nil_unicode(instance.glosary, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
        )

        return rst
