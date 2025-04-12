# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class GFPPlanoContaConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.gfp.planoconta"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.gfp.planoconta.views",
        "rh.gfp.planoconta.api.accountplan",
        "rh.gfp.planoconta.api.provisionplan",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/rh/gfp/accountplan/PlanRestful.js",
        "/%(context)s/static/rh/gfp/accountplan/PlanWindow.js",
        "/%(context)s/static/rh/gfp/accountplan/PlanGrid.js",
        "/%(context)s/static/rh/gfp/accountplan/PlanManage.js",
        "/%(context)s/static/rh/gfp/accountplan/AccountPlanRestful.js",
        "/%(context)s/static/rh/gfp/accountplan/AccountPlanWindow.js",
        "/%(context)s/static/rh/gfp/accountplan/AccountPlanGrid.js",
        "/%(context)s/static/rh/gfp/accountplan/AccountPlanManage.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionPlanManage.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionPlanRestful.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionPlanWindow.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionPlanGrid.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionEmployeeRestful.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionEmployeeWindow.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionEmployeeGrid.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionManagerManage.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionManagerRestful.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionManagerWindow.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionManagerGrid.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionRestful.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionWindow.js",
        "/%(context)s/static/rh/gfp/provisionplan/ProvisionGrid.js",
        "/%(context)s/static/rh/gfp/provisionplan/WindowProvisionGenerator.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    pass
