# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from workflow.models import Workflow


log = getLogger(__name__)


class WFLWWorkflowRestful(RestfulDRY):

    _model = Workflow

    force_upper = False

    exclude_fields = ["common_ptr"]

    force_persist_boolean_fields = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("workflow.workflow.Manage")')
