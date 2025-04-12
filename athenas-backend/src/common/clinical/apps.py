# -*- coding: utf-8 -*-
import importlib
from django import apps


class AppConfig(
    apps.AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "common.clinical"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "common.clinical.api.doctor",
        "common.clinical.api.manage",
        "common.clinical.api.naturalperson",
        "common.clinical.api.prescription",
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
        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/common/clinical/clinical.css")

    js_paths = [
        "/%(context)s/static/common/clinical/doctor/Restful.js",
        "/%(context)s/static/common/clinical/doctor/Window.js",
        "/%(context)s/static/common/clinical/doctor/Grid.js",
        "/%(context)s/static/common/clinical/doctor/Manage.js",
        "/%(context)s/static/common/clinical/naturalperson/Restful.js",
        "/%(context)s/static/common/clinical/naturalperson/Window.js",
        "/%(context)s/static/common/clinical/naturalperson/Grid.js",
        "/%(context)s/static/common/clinical/prescription/Restful.js",
        "/%(context)s/static/common/clinical/prescription/Window.js",
        "/%(context)s/static/common/clinical/prescription/Grid.js",
        "/%(context)s/static/common/clinical/prescription/Manage.js",
    ]

    for path in js_paths:
        Application.register_javascript(path, scope="common")
