# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import BlokeDocument
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class EJudBlokeDocument(Restful):

    _model = BlokeDocument

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "moment" in params:
            if params.get("moment") != "":
                params.update(moment=DateUtils.str_to_datetime(params.get("moment")))
            else:
                params.update(moment=None)

        if "modified_by" in params:
            if params.get("modified_by") != "":
                field = getattr(self.Model, "modified_by")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(modified_by=query.get(pk=params.get("modified_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(modified_by=None)

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

        if "rejection_fact" in params:
            if params.get("rejection_fact") != "":
                field = getattr(self.Model, "rejection_fact")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        rejection_fact=query.get(pk=params.get("rejection_fact"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(rejection_fact=None)

        if "created_at" in params:
            if params.get("created_at") != "":
                params.update(
                    created_at=DateUtils.str_to_datetime(params.get("created_at"))
                )
            else:
                params.update(created_at=None)

        if "modified_at" in params:
            if params.get("modified_at") != "":
                params.update(
                    modified_at=DateUtils.str_to_datetime(params.get("modified_at"))
                )
            else:
                params.update(modified_at=None)

        if "created_by" in params:
            if params.get("created_by") != "":
                field = getattr(self.Model, "created_by")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(created_by=query.get(pk=params.get("created_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(created_by=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            moment=nil_datetime(instance.moment, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            text=instance.text,
            bloke=nil_pk(instance.bloke, None),
            bloke_unicode=nil_unicode(instance.bloke, None),
            rejection_fact=nil_pk(instance.rejection_fact, None),
            rejection_fact_unicode=nil_unicode(instance.rejection_fact, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            cached_render=instance.cached_render,
        )

        return rst
