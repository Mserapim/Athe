# -*- coding: utf-8 -*-

from standard.api.classcode import STDClassCodeRestful


class GFPLoaderRestful(STDClassCodeRestful):

    def get_query(self):
        return super(GFPLoaderRestful, self).get_query().filter(typeof="LOADER")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.classcode.LoaderManage")')


class GFPCalculationRestful(STDClassCodeRestful):

    def get_query(self):
        return super(GFPLoaderRestful, self).get_query().filter(typeof="CALCULO")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.classcode.CalculationManage")')
