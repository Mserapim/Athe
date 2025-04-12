# -*- coding: utf-8 -*-
import datetime

from django.db.models import Q

from contrib.utils import getLogger
from rh.dayoff.classcodes.base import DayOffBase
from standard.models import RunCodeManager
from rh.models import Servidor

log = getLogger(__name__)


@RunCodeManager.register("dayoff-classcodes-birthdaybreak")
class BirthdayBreak(DayOffBase):

    def __init__(self, group_period, employee=None, **kwargs):
        super().__init__(group_period, employee, **kwargs)

        self.months_max_usufruct = group_period.configuration.months_max_usufruct

    def get_start_date_acquisition(self):
        date = None
        try:
            date = datetime.datetime(
                self.get_year_reference(),
                self.employee.pessoa_fisica.data_nascimento.month,
                self.employee.pessoa_fisica.data_nascimento.day,
            ).date()
        except ValueError:
            if (
                self.employee.pessoa_fisica.data_nascimento.month == 2
                and self.employee.pessoa_fisica.data_nascimento.day == 29
            ):
                date = datetime.datetime(
                    self.get_year_reference(),
                    self.employee.pessoa_fisica.data_nascimento.month,
                    self.employee.pessoa_fisica.data_nascimento.day - 1,
                ).date()
        return date

    def get_end_date_acquisition(self):
        return self.get_start_date_acquisition()

    def get_start_date_fruition(self):
        return self.get_start_date_acquisition()

    def get_days(self):
        return 1

    def validate_acquisition_period(self):
        """Este método realiza as validações para criação do período aquisitivo.

        Returns:
            bool:
        Raise:
            Exception: raise exception quando não passa pela validação
        """
        if not self.employee.pessoa_fisica.data_nascimento:
            raise Exception("Servidor não possui data de nascimento.")
        super(BirthdayBreak, self).validate_acquisition_period()
        return True
