# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Interested
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EJudInterested(Restful):

    _model = Interested

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "person" in params:
            if params.get("person") != "":
                field = getattr(self.Model, "person")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(person=query.get(pk=params.get("person")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(person=None)

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

        if "direct" in params:
            params.update(direct=params.get("direct", "off").lower() == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            person=nil_pk(instance.person, None),
            person_unicode=nil_unicode(instance.person, None),
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            icons=instance.icons,
            direct=instance.direct,
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
        )

        return rst
