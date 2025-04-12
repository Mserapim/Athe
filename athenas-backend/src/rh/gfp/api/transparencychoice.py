# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.gfp.models import TransparencyChoice, GroupEvents


log = getLogger(__name__)


class GFPTransparencyChoice(RestfulDRY):

    _model = TransparencyChoice

    exclude_fields = ["choice_ptr"]

    full_text_index = (
        "label__icontains",
        "app_label__icontains",
        "name__icontains",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.transparencychoice.Manage")')

    def model_to_dict(self, instance):
        rst = super(GFPTransparencyChoice, self).model_to_dict(instance)

        rst.update(group=instance.group)
        rst.update(group_unicode=instance.get_group_display())
        rst.update(active=instance.active)

        return rst


class GFPGroupEvents(RestfulDRY):

    _model = GroupEvents

    full_text_index = (
        "label__icontains",
        "app_label__icontains",
        "name__icontains",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.transparencychoice.GroupEventsManage")'
        )

    def model_to_dict(self, instance):
        rst = super(GFPGroupEvents, self).model_to_dict(instance)

        rst.update(group=instance.group)
        rst.update(group_unicode=instance.get_group_display())
        rst.update(active=instance.active)

        return rst
