# -*- coding: utf-8 -*-
import json
from contrib.controller import DefaultController
from default.views import Application as app


class UtilWaitingWorkController(DefaultController):

    @classmethod
    def register(klass, name):
        def wrapper(method):
            db = getattr(klass, "methods", {})
            db.update({name: method})
            klass.methods = db
            return method

        return wrapper

    def store(self, args=[]):
        methods = getattr(self.__class__, "methods", {})
        collection = []

        for name, method in list(methods.items()):
            data = method()
            if data.get("count", 0):
                data.update(keyId=name)
                collection.append(data)

        rst = {"success": True, "count": len(collection), "collection": collection}

        self.response.write(json.dumps(rst))

    @classmethod
    def report_waiting_works(klass):
        methods = getattr(klass, "methods", {})
        return sum([method().get("count") for method in list(methods.values())])


reg_waiting_work = UtilWaitingWorkController.register


@app.session_resource("waiting_work")
def __wrapper():
    return UtilWaitingWorkController.report_waiting_works()


"""
@reg_waiting_work('edoc')
def var1():
    return {
        'title': 'E-Doc a receber',
        'count': 2,
        'type': 'documentos'
    }

"""
