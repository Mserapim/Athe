# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class MediaIndoorConfig(AppConfig):
    name = "web.media_indoor"
    # label = 'media_indoor'
    verbose_name = "Mídia Indoor"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "web.media_indoor.api.device",
        "web.media_indoor.api.content",
        "web.media_indoor.api.contentlist",
        "web.media_indoor.api.campaign",
        "web.media_indoor.api.campaigngroup",
        "web.media_indoor.api.configcampaigngroup",
    ]

    def ready(self):
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():

    # from default.views import Application
    Application = importlib.import_module("default.views").Application

    js_paths = [
        "/%(context)s/static/web/media_indoor/device/Restful.js",
        "/%(context)s/static/web/media_indoor/device/Grid.js",
        "/%(context)s/static/web/media_indoor/device/Window.js",
        "/%(context)s/static/web/media_indoor/device/Manager.js",
        "/%(context)s/static/web/media_indoor/device/GroupWindow.js",
        "/%(context)s/static/web/media_indoor/content/Restful.js",
        "/%(context)s/static/web/media_indoor/content/Grid.js",
        "/%(context)s/static/web/media_indoor/content/Window.js",
        "/%(context)s/static/web/media_indoor/content/Manager.js",
        "/%(context)s/static/web/media_indoor/campaign/Restful.js",
        "/%(context)s/static/web/media_indoor/campaign/Grid.js",
        "/%(context)s/static/web/media_indoor/campaign/Window.js",
        "/%(context)s/static/web/media_indoor/campaign/Manager.js",
        "/%(context)s/static/web/media_indoor/campaign/CampaignManager.js",
        "/%(context)s/static/web/media_indoor/campaign/CampaignManagerWindow.js",
        "/%(context)s/static/web/media_indoor/content_list/Restful.js",
        "/%(context)s/static/web/media_indoor/content_list/Grid.js",
        "/%(context)s/static/web/media_indoor/content_list/Window.js",
        "/%(context)s/static/web/media_indoor/content_list/Manager.js",
        "/%(context)s/static/web/media_indoor/campaign_group/Restful.js",
        "/%(context)s/static/web/media_indoor/campaign_group/Grid.js",
        "/%(context)s/static/web/media_indoor/campaign_group/Window.js",
        "/%(context)s/static/web/media_indoor/campaign_group/Manager.js",
        "/%(context)s/static/web/media_indoor/campaign_group/CampaignGroupManager.js",
        "/%(context)s/static/web/media_indoor/config_campaign/Restful.js",
        "/%(context)s/static/web/media_indoor/config_campaign/Grid.js",
        "/%(context)s/static/web/media_indoor/config_campaign/Window.js",
        "/%(context)s/static/web/media_indoor/config_campaign/GroupWindow.js",
    ]

    for js_file in js_paths:
        Application.register_javascript(js_file, scope="web")

    # Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
