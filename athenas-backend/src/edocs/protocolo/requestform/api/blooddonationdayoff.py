# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.requestform.models import BloodDonationDayOff
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormBloodDonationDayOff(EDOCManage):

    _model = BloodDonationDayOff

    def model_to_dict(self, instance):
        data = super(RequestFormBloodDonationDayOff, self).model_to_dict(instance)

        form = instance.protocolo.blooddonationdayoff

        data.update(
            {
                "contact_number": (
                    form.contact_number if form.contact_number is not None else ""
                )
            }
        )

        return data
