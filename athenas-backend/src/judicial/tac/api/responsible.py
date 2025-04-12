# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.tac.models import Responsible
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class TacResponsible(Restful):

    _model = Responsible

    full_text_index = ("responsible_person__nome__icontains",)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "activity" in params:
            if params.get("activity") != "":
                field = getattr(self.Model, "activity")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(activity=query.get(pk=params.get("activity")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(activity=None)

        if "responsible_person" in params:
            if params.get("responsible_person") != "":
                field = getattr(self.Model, "responsible_person")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        responsible_person=query.get(
                            pk=params.get("responsible_person")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(responsible_person=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            activity=nil_pk(instance.activity, None),
            activity_unicode=nil_unicode(instance.activity, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            responsible_person=nil_pk(instance.responsible_person, None),
            responsible_person_unicode=nil_unicode(instance.responsible_person, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
        )

        return rst
