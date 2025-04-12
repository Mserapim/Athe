# -*- coding: utf-8 -*-
import re
import json

from contrib.controller import DefaultController
from standard.models import Configuration


class EJudConfiguration(DefaultController):

    def eval_value(self, value):
        if re.match(r"^\[.*\]$", value):
            return json.loads(value)
        else:
            return value

    def read(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        try:
            cfg = Configuration.get_or_create("ejud")
            rst.update(
                config={
                    item.key: self.eval_value(item.value) for item in cfg.items.filter()
                }
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        self.response.write(json.dumps(rst))

    def write(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        cfg = Configuration.get_or_create("ejud")

        cfg.set(self.request.POST.get("property"), self.request.POST.get("value"))

        self.response.write(json.dumps(rst))

    def save(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        try:
            cfg = Configuration.get_or_create("ejud")
            for attr in self.request.POST:
                cfg.set(attr, self.request.POST.get(attr))
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        self.response.write(json.dumps(rst))

    def json(self, args=[]):
        self.response.write('Ext._create("judicial.ConfigurationManage")')
