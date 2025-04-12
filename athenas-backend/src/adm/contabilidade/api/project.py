# -*- coding: utf-8 -*-
from adm.contabilidade.models import Project
from contrib.newrest import RestfulDRY


class ContabProject(RestfulDRY):

    _model = Project

    full_text_index = ("nome__icontains",)

    # exclude_fields = ['']

    # force_persist_boolean_fields = ['campo_booleano']

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("adm.contabilidade.project.Manage")')
