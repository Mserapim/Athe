# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.cirdir.models import Irpf

log = getLogger(__name__)


class CIRDIRIrpf(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = Irpf
