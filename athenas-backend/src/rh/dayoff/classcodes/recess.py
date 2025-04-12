# -*- coding: utf-8 -*-
from datetime import date

from contrib.utils import getLogger
from rh.dayoff.classcodes.base import DayOffBase
from standard.models import RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("dayoff-classcodes-recess")
class Recess(DayOffBase):

    def get_start_date_acquisition(self):
        if self.group_period.start_date_acquisition:
            return self.group_period.start_date_acquisition
        return date(self.group_period.year_reference, 12, 20)

    def get_end_date_acquisition(self):
        if self.group_period.start_date_acquisition:
            if self.group_period.end_date_acquisition:
                return self.group_period.end_date_acquisition
            else:
                return None
        return date(self.group_period.year_reference + 1, 1, 6)
