# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger

from common.saci.models import Attachment

log = getLogger(__name__)


class SACIAttachmentRestful(RestfulDRY):
    _model = Attachment

    # def get_query(self):
    #     query = super(SACIAttachmentRestful, self).get_query()

    #     employee = employee_from_user(self.request.user)

    #     work_locations = employee.work_locations.filter()

    #     return query.filter(
    #         pk__in=work_locations
    #     )
