# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import DismembermentMultiProcess
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class EjudDismembermentMultiProcess(BasePartLawsuit, Restful):

    _model = DismembermentMultiProcess
