# -*- coding: utf-8 -*-
from contrib.controller import DefaultController


class EJudManage(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("judicial.Manage")')


class EJudTriageManage(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("judicial.TriageManage")')


class EJudSecretaryManage(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("judicial.secretary.workspace.Manage")')
