# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import PersonHasAccess
from contrib.utils import DateUtils
from contrib.nil import nil_display, nil_pk, nil_unicode, nil_datetime

log = getLogger(__name__)


class EJudPersonHasAccess(Restful):

    _model = PersonHasAccess

    force_orm_single = True

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "access" in params:
            if params.get("access") != "":
                field = getattr(self.Model, "access")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(access=query.get(pk=params.get("access")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(access=None)

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

        if "replicate" in params:
            try:
                params.update(
                    replicate=True if params.get("replicate").lower() == "on" else False
                )
            except Exception as e:
                log.exception(e)
                raise e

        return params

    def factoryModel(self, *args, **kargs):
        value = kargs.get("replicate", False)
        if "replicate" in kargs:
            kargs.pop("replicate")
        inst = super(EJudPersonHasAccess, self).factoryModel(*args, **kargs)
        inst._replicate = value
        return inst

    def fill_instance_values(self, instance, values):
        flag = values.get("replicate", False)
        instance._replicate = flag
        super(EJudPersonHasAccess, self).fill_instance_values(instance, values)

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            access=nil_pk(instance.access, None),
            access_unicode=nil_unicode(instance.access, None),
            person=nil_pk(instance.person, None),
            person_unicode=nil_unicode(instance.person, None),
            icons=instance.icons,
            state=instance.state,
            state_display=nil_display(instance, "state", None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            finished_by=nil_pk(instance.finished_by, None),
            finished_by_unicode=nil_unicode(instance.finished_by, None),
            finished_at=nil_datetime(instance.finished_at, None),
            grant_by_system="SIM" if instance.grant_by_system else "NÃO",
            revoked_by_system="SIM" if instance.revoked_by_system else "NÃO",
        )

        return rst
