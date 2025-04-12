# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from workflow.models import PessoaVertex as PersonVertex


log = getLogger(__name__)


class WFLWPersonVertexRestful(RestfulDRY):

    _model = PersonVertex

    force_upper = False

    exclude_fields = ["common_ptr", "vertex_ptr"]

    force_persist_boolean_fields = ["active", "beginning"]
