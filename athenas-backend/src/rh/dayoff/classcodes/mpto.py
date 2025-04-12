# -*- coding: utf-8 -*-
from contrib.utils import getLogger, NewDateRange, DateUtils
from standard.models import RunCodeManager
from rh.models import Servidor
from rh.dayoff.models import Usufruct
from rh.dayoff.const import (
    USU_AUTORIZED_CI,
    USU_CANCELED,
    USU_CHANGED,
    USU_CHANGING,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_INTERRUPTED,
    USU_NEW,
    USU_NOT_AUTHORIZED,
    USU_SM,
    USU_SOLD,
    USU_SUBSTITUTE,
    USU_SUSPENDED,
)
from rh.dayoff.classcodes.base import DayOffBase


log = getLogger(__name__)


@RunCodeManager.register("dayoff-mpto")
class DayOffMpTo(DayOffBase):
    typeof = "DAYOFF"
    title = "Código de validações MPTO"
    description = ""

    def __init__(self, instance, **kwargs):
        self.instance = instance
        self.configure()

    def configure(self):
        pass

    def validate(self, *args, **kwargs):
        pass
