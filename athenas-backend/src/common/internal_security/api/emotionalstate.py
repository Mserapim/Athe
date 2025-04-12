# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from common.internal_security.models import EmotionalState


log = getLogger(__name__)


class ISecEmotionalState(RestfulDRY):
    _model = EmotionalState
