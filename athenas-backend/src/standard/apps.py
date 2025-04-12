# -*- coding:utf-8 -*-

import importlib
from django.apps import AppConfig


class StandardConfig(AppConfig):
    name = "standard"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "standard.views",
        "standard.api.classcode",
        "standard.api.choice",
        "standard.api.configuration",
        "standard.api.configpoint",
        "standard.api.emailtemplate",
    ]

    def ready(self):
        register_statics()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/standard/classcode/Restful.js",
        "/%(context)s/static/standard/classcode/Manage.js",
        "/%(context)s/static/standard/classcode/Grid.js",
        "/%(context)s/static/standard/classcode/Window.js",
        "/%(context)s/static/standard/ChoiceRestful.js",
        "/%(context)s/static/standard/ChoiceManage.js",
        "/%(context)s/static/standard/ChoiceGrid.js",
        "/%(context)s/static/standard/ChoiceWindow.js",
        "/%(context)s/static/standard/configuration/Restful.js",
        "/%(context)s/static/standard/configuration/Manage.js",
        "/%(context)s/static/standard/configuration/Grid.js",
        "/%(context)s/static/standard/configuration/Window.js",
        "/%(context)s/static/standard/configuration/item/Restful.js",
        "/%(context)s/static/standard/configuration/item/Manage.js",
        "/%(context)s/static/standard/configuration/item/Grid.js",
        "/%(context)s/static/standard/configuration/item/Window.js",
        "/%(context)s/static/standard/configuration/item/ManagerWindow.js",
        "/%(context)s/static/standard/configpoint/Restful.js",
        "/%(context)s/static/standard/configpoint/Manage.js",
        "/%(context)s/static/standard/configpoint/Grid.js",
        "/%(context)s/static/standard/configpoint/Window.js",
        "/%(context)s/static/standard/emailtemplate/Restful.js",
        "/%(context)s/static/standard/emailtemplate/Manage.js",
        "/%(context)s/static/standard/emailtemplate/Grid.js",
        "/%(context)s/static/standard/emailtemplate/Window.js",
        "/%(context)s/static/standard/configuration/item/justification/Restful.js",
        "/%(context)s/static/standard/configuration/item/justification/Manage.js",
        "/%(context)s/static/standard/configuration/item/justification/Grid.js",
        "/%(context)s/static/standard/configuration/item/justification/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="standard")
