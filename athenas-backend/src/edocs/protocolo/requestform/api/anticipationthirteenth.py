# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import AnticipationThirteenth
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormAnticipationThirteenth(EDOCManage):

    _model = AnticipationThirteenth

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("edocs.protocolo.requestform.anticipationthirteenth.Manage")'
        )

    def model_to_dict(self, instance):
        data = super(RequestFormAnticipationThirteenth, self).model_to_dict(instance)

        form = instance.protocolo.anticipationthirteenth

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                )
            }
        )

        return data
