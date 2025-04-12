# -*- coding: utf-8 -*-
import re
import json

from contrib.controller import DefaultController


class CIRDIRManagementHealthArea(DefaultController):

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.health.healtharea.ManagementHealthArea")'
        )
