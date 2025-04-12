# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from planejamento.contrato.models import Adtivo as Additive


log = getLogger(__name__)


class PHAAdditive(RestfulDRY):

    _model = Additive
