# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import NotificationHistory
import raf.api.util

log = getLogger(__name__)


class INSPECTIONNotificationHistory(RestfulDRY):

    force_upper = False

    full_text_index = ("protocol__codigo__icontains",)

    _model = NotificationHistory

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.analyse_recommendation.notificationhistory.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONNotificationHistory, self).model_to_dict(instance)
        _dict_.update(
            {
                "protocol_codigo": instance.protocol.codigo,
                "date": instance.created_at.strftime("%d/%m/%Y %H:%M"),
                "deadline": (
                    instance.deadline.strftime("%d/%m/%Y %H:%M")
                    if instance.deadline
                    else None
                ),
            }
        )
        return _dict_
