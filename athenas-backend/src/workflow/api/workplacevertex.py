# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from workflow.models import LotacaoVertex as WorkPlaceVertex


log = getLogger(__name__)


class WFLWWorkPlaceVertexRestful(RestfulDRY):

    _model = WorkPlaceVertex

    force_upper = False

    exclude_fields = ["common_ptr", "vertex_ptr"]

    force_persist_boolean_fields = ["active", "beginning"]
