# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class WorkflowConfig(AppConfig):
    name = "workflow"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "workflow.views",
        "workflow.api.edge",
        "workflow.api.joker",
        "workflow.api.jokervertex",
        "workflow.api.workplacevertex",
        "workflow.api.personvertex",
        "workflow.api.employeevertex",
        "workflow.api.vertex",
        "workflow.api.workflow_",
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

    Application.register_stylesheet("/%(context)s/static/workflow/css/styles.css")
    Application.register_stylesheet(
        "/%(context)s/static/workflow/images/workflow/wf.css"
    )

    js_paths = (
        "/%(context)s/static/workflow/edge/Restful.js",
        "/%(context)s/static/workflow/edge/Window.js",
        "/%(context)s/static/workflow/edge/Grid.js",
        "/%(context)s/static/workflow/joker/Restful.js",
        "/%(context)s/static/workflow/joker/Window.js",
        "/%(context)s/static/workflow/joker/Grid.js",
        "/%(context)s/static/workflow/vertex/Restful.js",
        "/%(context)s/static/workflow/vertex/Window.js",
        "/%(context)s/static/workflow/vertex/Grid.js",
        "/%(context)s/static/workflow/jokervertex/Restful.js",
        "/%(context)s/static/workflow/jokervertex/Window.js",
        "/%(context)s/static/workflow/jokervertex/Grid.js",
        "/%(context)s/static/workflow/workplacevertex/Restful.js",
        "/%(context)s/static/workflow/workplacevertex/Window.js",
        "/%(context)s/static/workflow/workplacevertex/Grid.js",
        "/%(context)s/static/workflow/personvertex/Restful.js",
        "/%(context)s/static/workflow/personvertex/Window.js",
        "/%(context)s/static/workflow/personvertex/Grid.js",
        "/%(context)s/static/workflow/employeevertex/Restful.js",
        "/%(context)s/static/workflow/employeevertex/Window.js",
        "/%(context)s/static/workflow/employeevertex/Grid.js",
        "/%(context)s/static/workflow/workflow/Restful.js",
        "/%(context)s/static/workflow/workflow/Window.js",
        "/%(context)s/static/workflow/workflow/Grid.js",
        "/%(context)s/static/workflow/workflow/Manage.js",
        "/%(context)s/static/workflow/js/main.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="core")
