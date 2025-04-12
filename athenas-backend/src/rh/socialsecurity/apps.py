# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class SocialSecurityConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.socialsecurity"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        # SOCIALSECURITY
        "rh.socialsecurity.api.employmentbond",
        "rh.socialsecurity.api.retirementprevision",
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

    Application.register_stylesheet(
        "/%(context)s/static/rh/images/socialsecurity/socialsecurity.css"
    )

    js_paths = (
        "/%(context)s/static/rh/socialsecurity/EmploymentBondRestful.js",
        "/%(context)s/static/rh/socialsecurity/EmploymentBondWindow.js",
        "/%(context)s/static/rh/socialsecurity/EmploymentBondGrid.js",
        "/%(context)s/static/rh/socialsecurity/RetirementPrevisionRestful.js",
        "/%(context)s/static/rh/socialsecurity/RetirementPrevisionWindow.js",
        "/%(context)s/static/rh/socialsecurity/RetirementPrevisionGrid.js",
        "/%(context)s/static/rh/socialsecurity/RetirementPrevisionManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    importlib.import_module("rh.socialsecurity.signals.rh_module")
