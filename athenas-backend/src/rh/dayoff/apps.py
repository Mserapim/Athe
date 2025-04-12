# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class DAYOFFConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.dayoff"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.dayoff.views",
        "rh.dayoff.reports",
        "rh.dayoff.api.configuration",
        "rh.dayoff.api.acquisitionperiod",
        "rh.dayoff.api.acquisitionperiodattachment",
        "rh.dayoff.api.groupperiod",
        "rh.dayoff.api.activity",
        "rh.dayoff.api.usufruct",
        "rh.dayoff.api.attachment",
        "rh.dayoff.api.payment",
        "rh.dayoff.api.reports",
        "rh.dayoff.api.mpmt.acquisitionperiod",
        "rh.dayoff.api.mpmt.acquisitionperiodattachment",
        "rh.dayoff.api.mpmt.activity",
        "rh.dayoff.api.mpmt.usufruct",
        "rh.dayoff.api.mpmt.payment_vacation",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    importlib.import_module("rh.dayoff.signals.departure")
    importlib.import_module("rh.dayoff.signals.usufruct")
    importlib.import_module("rh.dayoff.signals.acquisitionperiod")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui."""

    Application = importlib.import_module("default.views").Application

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/Manage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/sale/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/sale/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/sale/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/sale/Manage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/plantao_eleitoral/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/plantao_eleitoral/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/plantao_eleitoral/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/configuration/plantao_eleitoral/Manage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/groupperiod/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/groupperiod/Window.js"
    )
    Application.register_javascript("/%(context)s/static/rh/dayoff/groupperiod/Grid.js")
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/groupperiod/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/groupperiod/ManageExtended.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/ManageEmployee.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/ManageAdmin.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/HomologateWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/GroupFilterAction.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/TypeOfFilterAction.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/ConfigurationFilterAction.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/attachment/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/attachment/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/attachment/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/acquisitionperiod/attachment/Manage.js"
    )

    Application.register_javascript("/%(context)s/static/rh/dayoff/activity/Restful.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/activity/Window.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/activity/Grid.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/activity/Manage.js")
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/SpecializedWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/DetailWindow.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/AdminAuthorizeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/AdminAuthorizeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/AdminAuthorizeManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/AdminAuthorizeWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/AuthorizeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/AuthorizeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/AuthorizeManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/HomologateRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/HomologateGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/HomologateManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/MediateAuthorizeChartRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/MediateAuthorizeChartGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/MediateAuthorizeChartManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/MediateAuthorizeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/MediateAuthorizeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/authorization/MediateAuthorizeManage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/activity/sell/Manage.js"
    )

    Application.register_javascript("/%(context)s/static/rh/dayoff/usufruct/Restful.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/usufruct/Window.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/usufruct/Grid.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/usufruct/Manage.js")
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/usufruct/ConflictsWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/usufruct/ConflictsGrid.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/usufruct/employee/EmployeeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/usufruct/employee/EmployeeWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/usufruct/employee/EmployeeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/usufruct/employee/EmployeeManage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/attachment/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/attachment/Window.js"
    )
    Application.register_javascript("/%(context)s/static/rh/dayoff/attachment/Grid.js")
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/attachment/Manage.js"
    )

    Application.register_javascript("/%(context)s/static/rh/dayoff/payment/Restful.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/payment/Window.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/payment/Grid.js")
    Application.register_javascript("/%(context)s/static/rh/dayoff/payment/Manage.js")

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/reports/EnjoyedRecessesAndGaps.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/reports/HistoryRecessesAndGaps.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/reports/PendingRecessesAndGaps.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/reports/UsufructRecessesAndGaps.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/ManageEmployee.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/ManageAdmin.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/HomologateWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/GroupFilterAction.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/TypeOfFilterAction.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/ConfigurationFilterAction.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/attachment/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/attachment/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/attachment/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/acquisitionperiod/attachment/Manage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/SpecializedWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/DetailWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/ActivityWindow.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/AdminAuthorizeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/AdminAuthorizeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/AdminAuthorizeManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/AdminAuthorizeWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/AuthorizeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/AuthorizeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/AuthorizeManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/HomologateRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/HomologateGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/HomologateManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/MediateAuthorizeChartRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/MediateAuthorizeChartGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/MediateAuthorizeChartManage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/MediateAuthorizeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/MediateAuthorizeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/authorization/MediateAuthorizeManage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/sell/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/activity/PaymentWindow.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/Manage.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/ConflictsWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/ConflictsGrid.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/PaymentWindow.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/vacation/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/vacation/Window.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/vacation/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/vacation/Manage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/sell_vacation/Restful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/sell_vacation/Grid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/payment_vacation/sell_vacation/Manage.js"
    )

    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/employee/EmployeeRestful.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/employee/EmployeeWindow.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/employee/EmployeeGrid.js"
    )
    Application.register_javascript(
        "/%(context)s/static/rh/dayoff/mpmt/usufruct/employee/EmployeeManage.js"
    )


def loaders():
    pass
