# -*- coding: utf-8 -*-
from standard.api.choice import STDChoice
from judicial.models import JudicialChoice


class EJudJudicialChoice(STDChoice):

    _model = JudicialChoice

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.params.judicialchoice.Manage")')
