# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import SessionItem
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class CouncilSessionItem(Restful):

    _model = SessionItem

    force_upper = False

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "session" in params:
            if params.get("session") != "":
                field = getattr(self.Model, "session")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(session=query.get(pk=params.get("session")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(session=None)
        if "flag" in params:
            params.update(flag=params.get("flag", "off").lower() == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            text=instance.text,
            # part=nil_pk(instance.part, None),
            # part_unicode=nil_unicode(instance.part, None),
            session=nil_pk(instance.session, None),
            session_unicode=nil_unicode(instance.session, None),
            flag=instance.flag,
            title=instance.title,
        )

        return rst
