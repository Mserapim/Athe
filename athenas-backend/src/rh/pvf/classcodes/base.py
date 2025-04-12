# -*- coding: utf-8 -*-
from standard.models import RunCodeManager
from rh.pvf.models import STATUS_REQUEST, REQUEST_STEP


@RunCodeManager.register("pvf-base")
class PVFBase(object):
    pass
