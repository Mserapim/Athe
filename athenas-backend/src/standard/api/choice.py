# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.decorator import is_public
from standard.models import Choice


log = getLogger(__name__)


class STDChoice(RestfulDRY):

    _model = Choice

    force_upper = False

    full_text_index = ("cache_path__icontains",)

    @is_public()
    def v1(self, *args, **kwargs):
        super(STDChoice, self).v1(*args, **kwargs)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("standard.ChoiceManage")')

    def model_to_dict(self, instance):
        rst = super(STDChoice, self).model_to_dict(instance)

        rst.update(
            value=int(instance.value or 0),
        )

        return rst


class STDChoiceActive(STDChoice):

    full_text_index = ("cache_path__icontains",)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("standard.ChoiceManage")')

    def get_query(self):
        return super(STDChoiceActive, self).get_query().filter(active=True)
