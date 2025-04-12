# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.nil import nil_pk, nil_unicode
from judicial.models import Secretary, ExecutionOrgan


log = getLogger(__name__)


class EJudSecretary(RestfulDRY):

    _model = Secretary

    full_text_index = [
        "title__icontains",
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('judicial.secretary.Manage')")

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        rst.update(
            title=instance.title,
            location=nil_pk(instance.location, None),
            location_unicode=nil_unicode(instance.location, None),
        )

        return rst
