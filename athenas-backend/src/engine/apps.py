# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class EngineConfig(AppConfig):
    name = "engine"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "engine.views",
        "engine.api.controller",
        "engine.api.application",
        "engine.api.ldapserver",
        "engine.api.auth",
        "engine.api.group",
        "engine.api.permission",
        "engine.api.evento",
        "engine.api.dashboard",
    ]

    def ready(self):
        register_statics()
        # connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet(
        "/%(context)s/static/js/core/dashboard/dashboard.css"
    )
    Application.register_stylesheet("/%(context)s/static/css/river-panel.css")

    js_paths = (
        "/%(context)s/static/engine/js/core.js",
        "/%(context)s/static/engine/js/forms.js",
        "/%(context)s/static/engine/js/notification.js",
        "/%(context)s/static/js/crypto/md5.js",
        "/%(context)s/static/engine/evento/Manager.js",
        "/%(context)s/static/engine/evento/Restful.js",
        "/%(context)s/static/engine/evento/RestfulWindow.js",
        "/%(context)s/static/engine/evento/RestfulGrid.js",
        "/%(context)s/static/engine/ApplicationManage.js",
        "/%(context)s/static/engine/ApplicationRestful.js",
        "/%(context)s/static/engine/ApplicationWindow.js",
        "/%(context)s/static/engine/ApplicationTree.js",
        "/%(context)s/static/engine/ControllerRestful.js",
        "/%(context)s/static/engine/ControllerWindow.js",
        "/%(context)s/static/engine/ControllerGrid.js",
        "/%(context)s/static/js/auth/PermissionRestful.js",
        "/%(context)s/static/js/auth/PermissionWindow.js",
        "/%(context)s/static/js/auth/PermissionGrid.js",
        "/%(context)s/static/js/auth/GroupRestful.js",
        "/%(context)s/static/js/auth/GroupWindow.js",
        "/%(context)s/static/js/auth/GroupGrid.js",
        "/%(context)s/static/js/auth/GroupManage.js",
        "/%(context)s/static/js/auth/UserRestful.js",
        "/%(context)s/static/js/auth/UserWindow.js",
        "/%(context)s/static/js/auth/UserGrid.js",
        "/%(context)s/static/js/auth/UserEmployeeWindow.js",
        "/%(context)s/static/js/auth/UserManage.js",
        "/%(context)s/static/engine/LDAPServerRestful.js",
        "/%(context)s/static/engine/LDAPServerWindow.js",
        "/%(context)s/static/engine/LDAPServerGrid.js",
        "/%(context)s/static/engine/LDAPServerManage.js",
        "/%(context)s/static/engine/ControllerPermissionRestful.js",
        "/%(context)s/static/engine/ControllerPermissionWindow.js",
        "/%(context)s/static/engine/ControllerPermissionGrid.js",
        "/%(context)s/static/engine/ControllerPermissionManage.js",
        "/%(context)s/static/engine/task/TaskSessionRestful.js",
        "/%(context)s/static/engine/task/TaskSessionWindow.js",
        "/%(context)s/static/engine/task/TaskSessionGrid.js",
        "/%(context)s/static/engine/task/TaskSessionManage.js",
        "/%(context)s/static/engine/task/TaskMessageRestful.js",
        "/%(context)s/static/engine/task/TaskMessageWindow.js",
        "/%(context)s/static/engine/task/TaskMessageGrid.js",
        "/%(context)s/static/engine/task/TaskMessageManage.js",
        "/%(context)s/static/engine/task/TaskRunner.js",
        "/%(context)s/static/js/core/utils/LoadMaskMixin.js",
        "/%(context)s/static/js/core/utils/BoxMessage.js",
        "/%(context)s/static/js/core/dashboard/CustomPanel.js",
        "/%(context)s/static/js/core/dashboard/userinfo/PhoneCRUDWindow.js",
        "/%(context)s/static/js/core/dashboard/userinfo/UserInformationPanel.js",
        "/%(context)s/static/js/core/dashboard/PendentWorkGrid.js",
        "/%(context)s/static/js/core/dashboard/notification/Window.js",
        "/%(context)s/static/js/core/dashboard/notification/ListView.js",
        "/%(context)s/static/js/core/dashboard/notification/Panel.js",
        "/%(context)s/static/js/core/dashboard/tasksondemand/DropdownMenu.js",
        "/%(context)s/static/js/core/dashboard/EmployeePortalPanel.js",
        "/%(context)s/static/js/core/dashboard/Container.js",
        "/%(context)s/static/js/core/dashboard/Manager.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="core")
