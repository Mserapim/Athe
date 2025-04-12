# -*- coding: utf-8 -*-
import json

from contrib.controller import DefaultController
from contrib.newrest import Restful
from contrib.utils import getLogger

log = getLogger(__name__)


class CNMPManage(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.cnmp.Manage")')
