# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class CorregedoriaConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "corregedoria"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "corregedoria.api.configuration",
        "corregedoria.api.productivity",
        "corregedoria.api.scoretable",
        "corregedoria.api.bandscoretable",
        "corregedoria.api.linkinspectionraf",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app
        load_notify()


def load_notify():
    importlib.import_module("corregedoria.notify")


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

    js_paths = (
        "/%(context)s/static/corregedoria/Configuration.js",
        "/%(context)s/static/corregedoria/productivity/Grid.js",
        "/%(context)s/static/corregedoria/productivity/Restful.js",
        "/%(context)s/static/corregedoria/productivity/Window.js",
        "/%(context)s/static/corregedoria/scoretable/Grid.js",
        "/%(context)s/static/corregedoria/scoretable/Restful.js",
        "/%(context)s/static/corregedoria/scoretable/Window.js",
        "/%(context)s/static/corregedoria/scoretable/ListBandScoreTableWindow.js",
        "/%(context)s/static/corregedoria/scoretable/bandscoretable/Grid.js",
        "/%(context)s/static/corregedoria/scoretable/bandscoretable/Restful.js",
        "/%(context)s/static/corregedoria/scoretable/bandscoretable/Window.js",
        "/%(context)s/static/corregedoria/linkinspectionraf/Grid.js",
        "/%(context)s/static/corregedoria/linkinspectionraf/Restful.js",
        "/%(context)s/static/corregedoria/linkinspectionraf/Window.js",
        "/%(context)s/static/corregedoria/inspection/attachment/AttachmentGrid.js",
        "/%(context)s/static/corregedoria/inspection/attachment/AttachmentRestful.js",
        "/%(context)s/static/corregedoria/inspection/attachment/AttachmentWindow.js",
        "/%(context)s/static/corregedoria/inspection/attachment/Manage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="corregedoria")

    Application.register_stylesheet("/%(context)s/static/corregedoria/crgmpe.css")
