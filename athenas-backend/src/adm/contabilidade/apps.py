# -*- coding:utf-8 -*-

import importlib

from django.apps import AppConfig


class AccountingConfig(AppConfig):
    name = "adm.contabilidade"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "adm.contabilidade.views",
        "adm.contabilidade.api.fonterecurso",
        "adm.contabilidade.api.ppaacao",
        "adm.contabilidade.api.ne",
        "adm.contabilidade.api.ppaprograma",
        "adm.contabilidade.api.pparevisao",
        "adm.contabilidade.api.budgetaryindicator",
        "adm.contabilidade.api.unity",
        "adm.contabilidade.api.product",
    ]

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/adm/js/core.js",
        "/%(context)s/static/adm/contabilidade/NERestful.js",
        "/%(context)s/static/adm/contabilidade/NEWindow.js",
        "/%(context)s/static/adm/contabilidade/NEGrid.js",
        "/%(context)s/static/adm/contabilidade/NEManage.js",
        # '/%(context)s/static/adm/daily/financeiro/ProcessoPPAAcaoRestful.js',
        # '/%(context)s/static/adm/daily/financeiro/ProcessoPPAAcaoWindow.js',
        # '/%(context)s/static/adm/daily/financeiro/ProcessoPPAAcaoGrid.js',
        "/%(context)s/static/adm/contabilidade/PPAProgramaRestful.js",
        "/%(context)s/static/adm/contabilidade/PPAProgramaWindow.js",
        "/%(context)s/static/adm/contabilidade/PPAProgramaGrid.js",
        "/%(context)s/static/adm/contabilidade/PPAAcaoRestful.js",
        "/%(context)s/static/adm/contabilidade/PPAAcaoWindow.js",
        "/%(context)s/static/adm/contabilidade/PPAAcaoGrid.js",
        "/%(context)s/static/adm/contabilidade/PPARevisaoRestful.js",
        "/%(context)s/static/adm/contabilidade/PPARevisaoWindow.js",
        "/%(context)s/static/adm/contabilidade/PPARevisaoGrid.js",
        "/%(context)s/static/adm/contabilidade/FonteRecursoRestful.js",
        "/%(context)s/static/adm/contabilidade/FonteRecursoWindow.js",
        "/%(context)s/static/adm/contabilidade/FonteRecursoGrid.js",
        "/%(context)s/static/adm/contabilidade/budgetaryindicator/Restful.js",
        "/%(context)s/static/adm/contabilidade/budgetaryindicator/Window.js",
        "/%(context)s/static/adm/contabilidade/budgetaryindicator/Grid.js",
        "/%(context)s/static/adm/contabilidade/product/Restful.js",
        "/%(context)s/static/adm/contabilidade/product/Window.js",
        "/%(context)s/static/adm/contabilidade/product/Grid.js",
        "/%(context)s/static/adm/contabilidade/product/Manage.js",
        "/%(context)s/static/adm/contabilidade/unity/Restful.js",
        "/%(context)s/static/adm/contabilidade/unity/Window.js",
        "/%(context)s/static/adm/contabilidade/unity/Grid.js",
        "/%(context)s/static/adm/contabilidade/unity/Manage.js",
        "/%(context)s/static/adm/contabilidade/PPAManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="adm")
