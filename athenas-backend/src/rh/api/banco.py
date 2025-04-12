# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Banco as Bank


class RHBank(RestfulDRY):

    full_text_index = (
        "nome__icontains",
        "numero__icontains",
    )

    _model = Bank

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.bank.BankManage")')


class RHBankCovenant(RHBank):

    def get_query(self):
        return super(RHBankCovenant, self).get_query().filter(tem_convenio=True)
