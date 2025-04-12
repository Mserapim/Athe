# -*- coding: utf-8 -*-
from adm.contabilidade.models import BudgetaryIndicator
from contrib.newrest import RestfulDRY


class ContabBudgetaryIndicator(RestfulDRY):

    _model = BudgetaryIndicator

    full_text_index = (
        "name__icontains",
        "object_name__icontains",
        "action__codigo__icontains",
        "action__titulo__icontains",
    )

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("adm.contabilidade.budgetaryindicator.Manage")'
        )
