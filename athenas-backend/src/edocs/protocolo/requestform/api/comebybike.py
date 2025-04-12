# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import ComeByBike
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormComeByBike(EDOCManage):

    _model = ComeByBike
