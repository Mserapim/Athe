# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import Servidor


log = getLogger(__name__)


class PRONTUARYEmployee(RestfulDRY):

    _model = Servidor

    full_text_index = (
        "matricula__icontains",
        "pessoa_fisica__nome__icontains",
    )
