# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from workflow.models import Joker


log = getLogger(__name__)


class WFLWJokerRestful(RestfulDRY):

    _model = Joker

    force_upper = False

    exclude_fields = ["common_ptr"]

    force_persist_boolean_fields = ["active"]
