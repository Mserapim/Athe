# -*- coding: utf-8 -*-
import json

from contrib.newrest import Restful
from contrib.utils import getLogger
from auditoria.models import LineLog
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class AuditaLineLog(Restful):

    _model = LineLog

    full_text_index = (
        "controller__icontains",
        "action__icontains",
        "user__username__icontains",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("auditoria.LineLogManage")')

    def do_post(self, *args, **kargs):
        raise Exception(
            "Ação de criação não autorizada.".encode("ascii", "xmlcharrefreplace")
        )

    def do_put(self, *args, **kargs):
        raise Exception(
            "Ação de edição não autorizada.".encode("ascii", "xmlcharrefreplace")
        )

    def do_delete(self, *args, **kargs):
        raise Exception(
            "Ação de deleção não autorizada.".encode("ascii", "xmlcharrefreplace")
        )

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "user" in params:
            if params.get("user") != "":
                field = getattr(self.Model, "user")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(user=query.get(pk=params.get("user")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(user=None)

        if "dt" in params:
            if params.get("dt") != "":
                params.update(dt=DateUtils.str_to_datetime(params.get("dt")))
            else:
                params.update(dt=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            status=instance.status,
            status_display=nil_display(instance, "status", None),
            controller=(
                instance.controller if instance.controller else "Nível de modelo"
            ),
            user=nil_pk(instance.user, None),
            user_unicode=nil_unicode(instance.user, None),
            level=instance.level,
            level_display=nil_display(instance, "level", None),
            action=instance.action if instance.action else "Nível de modelo",
            json_description="<pre><code>%s</code></pre>"
            % json.dumps(json.loads(instance.json_description), indent=4),
            dt=nil_datetime(instance.dt, None),
            host_address=instance.host_address,
            host_name=instance.host_name,
        )

        return rst
