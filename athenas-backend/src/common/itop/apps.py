# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class ItopConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "common.itop"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        # iTop
        "common.itop.api.userrequest",
        "common.itop.api.quickcontent",
    ]

    def ready(self):
        # connect_signals()
        # load_notify()
        register_statics()


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:
        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    """Registro dos Stylesheet para este aplicativo"""
    Application.register_stylesheet("/%(context)s/static/common/itop/itop.css")

    js_paths = (
        "/%(context)s/static/common/itop/userrequest/UserRequestManage.js",
        "/%(context)s/static/common/itop/userrequest/UserRequestGrid.js",
        "/%(context)s/static/common/itop/userrequest/UserRequestWindow.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
