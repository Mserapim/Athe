# -*- coding: utf-8 -*-
from contrib.newrest import Restful


class PATManage(Restful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("adm.patrimonio.Manage")')
