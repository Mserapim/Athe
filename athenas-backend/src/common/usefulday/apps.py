# -*- coding:utf-8 -*-
"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class UsefuldayConfig(AppConfig):
    name = "common.usefulday"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "common.usefulday.api.nonworkingday",
    ]

    def ready(self):
        register_statics()
        # connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet(
        "/%(context)s/static/common/usefulday/images/usefulday.css"
    )

    js_paths = (
        "/%(context)s/static/common/usefulday/nonworkingday/NonWorkingDayGrid.js",
        "/%(context)s/static/common/usefulday/nonworkingday/NonWorkingDayRestful.js",
        "/%(context)s/static/common/usefulday/nonworkingday/NonWorkingDayHolidayWindow.js",
        "/%(context)s/static/common/usefulday/nonworkingday/NonWorkingDaySuspensionWindow.js",
        "/%(context)s/static/common/usefulday/nonworkingday/NonWorkingDayRecessWindow.js",
        "/%(context)s/static/common/usefulday/nonworkingday/NonWorkingDayManage.js",
        "/%(context)s/static/common/usefulday/nonworkingday/NonWorkingDayCopy.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
