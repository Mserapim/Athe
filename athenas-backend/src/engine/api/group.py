# -*- coding: utf-8 -*-
from app.settings import AUTO_PERMISSIONS_GROUPS
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from django.contrib.auth.models import Group
from engine.models import GroupPermission


log = getLogger(__name__)


class AuthGroup(RestfulDRY):

    if AUTO_PERMISSIONS_GROUPS:
        _model = GroupPermission
    else:
        _model = Group

    full_text_index = ("name__icontains",)

    force_upper = False

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'Ext._create("auth.GroupManage", {autoPermissionsGroups: "%s"})'
            % (AUTO_PERMISSIONS_GROUPS)
        )

    def model_to_dict(self, instance):
        params = super(AuthGroup, self).model_to_dict(instance)

        params.update({"auto_permissions_groups": AUTO_PERMISSIONS_GROUPS})
        return params
