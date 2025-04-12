# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from engine.models import LDAPServer
from contrib.nil import nil_display


log = getLogger(__name__)


class ENGLDAPServerRestful(Restful):

    _model = LDAPServer

    force_upper = False

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("engine.LDAPServerManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "tls" in params:
            params.update(tls=params.get("tls", "off").lower() == "on")

        if "falt" in params:
            params.update(falt=params.get("falt", "off").lower() == "on")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            dn=instance.dn,
            priority=instance.priority,
            priority_display=nil_display(instance, "priority", None),
            admin_user=instance.admin_user,
            admin_password=instance.admin_password,
            address=instance.address,
            tls=instance.tls,
            user_object=instance.user_object,
            basedn=instance.basedn,
            port=instance.port,
            falt=instance.falt,
        )

        return rst
