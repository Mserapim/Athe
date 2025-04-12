# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class RegistrationConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.registration"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.registration.api.registration"
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:


        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/rh/registration/forminformation/Manage.js",
        "/%(context)s/static/rh/registration/forminformation/Grid.js",
        "/%(context)s/static/rh/registration/forminformation/Restful.js",
        "/%(context)s/static/rh/registration/forminformation/Window.js",
        "/%(context)s/static/rh/registration/forminformation/Report.js",
        "/%(context)s/static/rh/registration/forminformation/general/Manage.js",
        "/%(context)s/static/rh/registration/forminformation/general/Grid.js",
        "/%(context)s/static/rh/registration/forminformation/general/Restful.js",
        "/%(context)s/static/rh/registration/forminformation/general/Window.js",
        "/%(context)s/static/rh/registration/forminformation/admin/Manage.js",
        "/%(context)s/static/rh/registration/forminformation/admin/Grid.js",
        "/%(context)s/static/rh/registration/forminformation/admin/Restful.js",
        "/%(context)s/static/rh/registration/forminformation/admin/Window.js",
        "/%(context)s/static/rh/registration/forminformation/admin/DependenteGrid.js",
        "/%(context)s/static/rh/registration/forminformation/admin/DependenteRestful.js",
        "/%(context)s/static/rh/registration/forminformation/admin/DependenteWindow.js",
        "/%(context)s/static/rh/registration/forminformation/admin/WindowMessageValidation.js",
        "/%(context)s/static/rh/registration/forminformation/ged/Grid.js",
        "/%(context)s/static/rh/registration/forminformation/ged/Admin.js",
        "/%(context)s/static/rh/registration/forminformation/ged/Window.js",
        "/%(context)s/static/rh/registration/forminformation/validation/Restful.js",
        "/%(context)s/static/rh/registration/forminformation/validation/Grid.js",
        "/%(context)s/static/rh/registration/forminformation/validation/Window.js",
        "/%(context)s/static/rh/registration/forminformation/dependente/DependenteManage.js",
        "/%(context)s/static/rh/registration/forminformation/dependente/DependenteRestful.js",
        "/%(context)s/static/rh/registration/forminformation/dependente/DependenteGrid.js",
        "/%(context)s/static/rh/registration/forminformation/dependente/DependenteWindow.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")
