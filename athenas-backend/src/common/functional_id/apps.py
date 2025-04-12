# -*- coding: utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django import apps


class AppConfig(
    apps.AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "common.functional_id"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = ["common.functional_id.api.functionalid"]

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
        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet(
        "/%(context)s/static/common/functionalId/common.css"
    )
    Application.register_stylesheet(
        "/%(context)s/static/common/functionalId/preview.css"
    )

    js_paths = (
        "/%(context)s/static/common/functionalId/Restful.js",
        "/%(context)s/static/common/functionalId/Window.js",
        "/%(context)s/static/common/functionalId/Grid.js",
        "/%(context)s/static/common/functionalId/Manage.js",
        "/%(context)s/static/common/functionalId/PendentSignManage.js",
        "/%(context)s/static/common/functionalId/Configuration.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
