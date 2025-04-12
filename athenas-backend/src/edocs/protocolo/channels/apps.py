# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class ProtocolChannelsConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "edocs.protocolo.channels"  # Caminho completo para o app. Ex: rh.gfp.dirf
    label = "protocol_channels"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "edocs.protocolo.channels.api",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    # importlib.import_module('edocs.protocolo.signals.distributiontable')
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    Application.register_javascript(
        "/%(context)s/static/edocs/channels/ChannelsRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/edocs/channels/ChannelsManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/edocs/channels/ChannelsGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/edocs/channels/ChannelsWindow.js"
    )
