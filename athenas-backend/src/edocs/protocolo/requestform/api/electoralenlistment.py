# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import ElectoralEnlistment
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormElectoralEnlistment(EDOCManage):

    _model = ElectoralEnlistment

    def model_to_dict(self, instance):
        data = super(RequestFormElectoralEnlistment, self).model_to_dict(instance)

        form = instance.protocolo.electoralenlistment

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                )
            }
        )

        return data
