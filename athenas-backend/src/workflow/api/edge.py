# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from workflow.models import Edge


log = getLogger(__name__)


class WFLWEdgeRestful(RestfulDRY):

    _model = Edge

    exclude_fields = ["edge_hash"]

    force_upper = False
