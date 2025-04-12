# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import TriagePartLocation
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudTriagePartLocation(Restful):

    _model = TriagePartLocation

    force_orm_single = True

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "sectional" in params:
            if params.get("sectional") != "":
                field = getattr(self.Model, "sectional")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(sectional=query.get(pk=params.get("sectional")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(sectional=None)

        if "triagepart" in params:
            if params.get("triagepart") != "":
                field = getattr(self.Model, "triagepart")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(triagepart=query.get(pk=params.get("triagepart")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(triagepart=None)

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

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            sectional=nil_pk(instance.sectional, None),
            sectional_unicode=nil_unicode(instance.sectional, None),
            triagepart=nil_pk(instance.triagepart, None),
            triagepart_unicode=nil_unicode(instance.triagepart, None),
            location=nil_pk(instance.location, None),
            location_unicode=nil_unicode(instance.location, None),
        )

        return rst
