# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import Character


log = getLogger(__name__)


class EJudCharacter(Restful):

    _model = Character

    force_upper = False

    full_text_index = (
        "title__icontains",
        "slug__icontains",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.params.CharacterManage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(slug=instance.slug, title=instance.title)

        return rst
