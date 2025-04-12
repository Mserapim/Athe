# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class WebConfig(AppConfig):
    name = "web"
    verbose_name = "Web"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "web.views",
        "web.services.views",
        "web.docsverify.views",
        "web.rpc.account",
        "web.rpc.polls",
        "web.rpc.ombudsman.server",
        "web.rpc.docsverify",
        "web.api.cms.area",
        "web.api.cms.metadata",
        "web.api.cms.category",
        "web.api.cms.post",
        "web.api.cms.file",
        "web.api.cms.comment",
        "web.api.intranet.icons",
        "web.api.intranet.intranet",
        "web.api.intranet.post",
        "web.api.intranet.link",
        "web.api.intranet.category",
        "web.api.intranet.metadado",
        "web.api.intranet.poll",
        "web.api.intranet.webgroup",
    ]

    def ready(self):
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("web.signals")


def register_statics():

    # from default.views import Application
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/web/js/shortcuts.js",
        "/%(context)s/static/web/js/misc.js",
        "/%(context)s/static/web/js/core.js",
        "/%(context)s/static/web/js/cms-sites.js",
        "/%(context)s/static/web/js/cms-areas.js",
        "/%(context)s/static/web/js/cms-links.js",
        "/%(context)s/static/web/js/cms-posts.js",
        "/%(context)s/static/web/js/cms-polls.js",
        "/%(context)s/static/web/js/cms-pgj-actions.js",
        "/%(context)s/static/web/js/cms-pgj-action-status.js",
        "/%(context)s/static/web/js/cms-attachments.js",
        "/%(context)s/static/web/js/cms-permissions.js",
        "/%(context)s/static/web/js/conf.js",
        "/%(context)s/static/web/js/intranet.js",
        "/%(context)s/static/web/intranet/BasicHome.js",
        "/%(context)s/static/web/intranet/Grid.js",
        "/%(context)s/static/web/intranet/Manage.js",
        "/%(context)s/static/web/intranet/Restful.js",
        "/%(context)s/static/web/intranet/Window.js",
        "/%(context)s/static/web/intranet/Tree.js",
        "/%(context)s/static/web/intranet/post/Grid.js",
        "/%(context)s/static/web/intranet/post/Manage.js",
        "/%(context)s/static/web/intranet/post/Restful.js",
        "/%(context)s/static/web/intranet/post/Window.js",
        "/%(context)s/static/web/intranet/link/Grid.js",
        "/%(context)s/static/web/intranet/link/Manage.js",
        "/%(context)s/static/web/intranet/link/Restful.js",
        "/%(context)s/static/web/intranet/link/Window.js",
        "/%(context)s/static/web/intranet/category/Grid.js",
        "/%(context)s/static/web/intranet/category/Manage.js",
        "/%(context)s/static/web/intranet/category/Restful.js",
        "/%(context)s/static/web/intranet/category/Window.js",
        "/%(context)s/static/web/intranet/metadado/Grid.js",
        "/%(context)s/static/web/intranet/metadado/Manage.js",
        "/%(context)s/static/web/intranet/metadado/Restful.js",
        "/%(context)s/static/web/intranet/metadado/Window.js",
        "/%(context)s/static/web/intranet/poll/Grid.js",
        "/%(context)s/static/web/intranet/poll/Manage.js",
        "/%(context)s/static/web/intranet/poll/Restful.js",
        "/%(context)s/static/web/intranet/poll/Window.js",
        "/%(context)s/static/web/intranet/webgroup/Grid.js",
        "/%(context)s/static/web/intranet/webgroup/Manage.js",
        "/%(context)s/static/web/intranet/webgroup/Restful.js",
        "/%(context)s/static/web/intranet/webgroup/Window.js",
        "/%(context)s/static/web/intranet/icons/Restful.js",
        "/%(context)s/static/web/intranet/icons/Window.js",
        "/%(context)s/static/web/intranet/icons/Grid.js",
        "/%(context)s/static/web/intranet/icons/Manage.js",
        "/%(context)s/static/web/js/cms/area/Restful.js",
        "/%(context)s/static/web/js/cms/area/Window.js",
        "/%(context)s/static/web/js/cms/area/Grid.js",
        "/%(context)s/static/web/js/cms/area/Manager.js",
        "/%(context)s/static/web/js/cms/metadata/MetaKeyRestful.js",
        "/%(context)s/static/web/js/cms/metadata/MetaKeyWindow.js",
        "/%(context)s/static/web/js/cms/metadata/MetaKeyGrid.js",
        "/%(context)s/static/web/js/cms/metadata/MetaKeyManager.js",
        "/%(context)s/static/web/js/cms/metadata/MetaValueRestful.js",
        "/%(context)s/static/web/js/cms/metadata/MetaValueWindow.js",
        "/%(context)s/static/web/js/cms/metadata/MetaValueGrid.js",
        "/%(context)s/static/web/js/cms/metadata/MetaValueManager.js",
        "/%(context)s/static/web/js/cms/category/Restful.js",
        "/%(context)s/static/web/js/cms/category/Window.js",
        "/%(context)s/static/web/js/cms/category/Grid.js",
        "/%(context)s/static/web/js/cms/category/Manager.js",
        "/%(context)s/static/web/js/cms/post/Restful.js",
        "/%(context)s/static/web/js/cms/post/Window.js",
        "/%(context)s/static/web/js/cms/post/ClassifyYearWindow.js",
        "/%(context)s/static/web/js/cms/post/ClassifyCategoryWindow.js",
        "/%(context)s/static/web/js/cms/post/Grid.js",
        "/%(context)s/static/web/js/cms/post/Manager.js",
        "/%(context)s/static/web/js/cms/contentarea/Restful.js",
        "/%(context)s/static/web/js/cms/contentarea/Window.js",
        "/%(context)s/static/web/js/cms/contentarea/Grid.js",
        "/%(context)s/static/web/js/cms/contentarea/Manager.js",
        "/%(context)s/static/web/js/cms/file/Restful.js",
        "/%(context)s/static/web/js/cms/file/Window.js",
        "/%(context)s/static/web/js/cms/file/ApplyMonthWindow.js",
        "/%(context)s/static/web/js/cms/file/Grid.js",
        "/%(context)s/static/web/js/cms/file/Manager.js",
        "/%(context)s/static/web/js/cms/intranet/MenuManager.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="web")

    Application.register_stylesheet("/%(context)s/static/web/css/styles.css")
