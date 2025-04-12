# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from judicial.models import NoticeConfiguration

log = getLogger(__name__)


class EJudNoticeConfiguration(RestfulDRY):
    _model = NoticeConfiguration
    full_text_index = [
        "legal_classification__path_cache__icontains",
        "legal_classification__title__icontains",
        "departament__sigla__icontains",
        "departament__nome__icontains",
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('judicial.noticeconfiguration.Manage')")

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        rst = {**rst, "departament_display": instance.departament_display}

        return rst
