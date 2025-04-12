# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from edocs.protocolo.models import Attachment
from contrib.nil import nil_pk, nil_unicode, nil_datetime


log = getLogger(__name__)


class EDOCAttachment(Restful):

    _model = Attachment

    force_upper = False

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "attach" in params:
            if params.get("attach") != "":
                field = getattr(self.Model, "attach")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(attach=query.get(pk=params.get("attach")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(attach=None)

        if "moviment" in params:
            if params.get("moviment") != "":
                field = getattr(self.Model, "moviment")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(moviment=query.get(pk=params.get("moviment")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(moviment=None)

        if "protocol" in params:
            if params.get("protocol") != "":
                field = getattr(self.Model, "protocol")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(protocol=query.get(pk=params.get("protocol")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(protocol=None)

        params.update(observation=" ")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            attach=nil_pk(instance.attach, None),
            attach_unicode=nil_unicode(instance.attach, None),
            attach_url=(
                instance.attach.complete_permalink()
                if hasattr(instance, "attach")
                else None
            ),
            moviment=nil_pk(instance.moviment, None),
            moviment_unicode=nil_unicode(instance.moviment, None),
            protocol=nil_pk(instance.protocol, None),
            protocol_unicode=nil_unicode(instance.protocol, None),
            observation=instance.observation,
            title=instance.title,
        )

        return rst
