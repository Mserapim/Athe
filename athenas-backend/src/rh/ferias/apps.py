# -*- coding:utf-8 -*-
"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""
import importlib

from django.apps import AppConfig


class FRSConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.ferias"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.ferias.views",
        "rh.ferias.reports",
        "rh.ferias.api.pas",
        "rh.ferias.api.configuration",
        "rh.ferias.api.reports",
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
        "/%(context)s/static/rh/js/ferias.js",
        "/%(context)s/static/rh/js/ferias.gerenciador.js",
        "/%(context)s/static/rh/js/ferias.gerenciador.fopag.js",
        "/%(context)s/static/rh/ferias/configuration/message/Restful.js",
        "/%(context)s/static/rh/ferias/configuration/message/Panel.js",
        "/%(context)s/static/rh/ferias/configuration/message/Manager.js",
        "/%(context)s/static/rh/ferias/configuration/Restful.js",
        "/%(context)s/static/rh/ferias/configuration/Grid.js",
        "/%(context)s/static/rh/ferias/configuration/Window.js",
        "/%(context)s/static/rh/ferias/configuration/Manage.js",
        "/%(context)s/static/rh/ferias/pas/EmployeeAcquisitionPeriodRestful.js",
        "/%(context)s/static/rh/ferias/pas/EmployeeAcquisitionPeriodGrid.js",
        "/%(context)s/static/rh/ferias/pas/EmployeeAcquisitionPeriodWindow.js",
        "/%(context)s/static/rh/ferias/pas/EmployeeAcquisitionPeriodManage.js",
        "/%(context)s/static/rh/ferias/pas/EmployeeAcquisitionPeriodSpecialized.js",
        "/%(context)s/static/rh/ferias/pas/AcquisitionPeriodRestful.js",
        "/%(context)s/static/rh/ferias/pas/AcquisitionPeriodGrid.js",
        "/%(context)s/static/rh/ferias/pas/AcquisitionPeriodWindow.js",
        "/%(context)s/static/rh/ferias/pas/AcquisitionPeriodManage.js",
        "/%(context)s/static/rh/ferias/reports/Collaborator.js",
        "/%(context)s/static/rh/ferias/reports/HolidayHistory.js",
        "/%(context)s/static/rh/ferias/reports/PendingHolidays.js",
        "/%(context)s/static/rh/ferias/reports/UnmarkedScales.js",
        "/%(context)s/static/rh/ferias/reports/HomologationMembros.js",
        "/%(context)s/static/rh/ferias/reports/HomologationEmployee.js",
        "/%(context)s/static/rh/ferias/reports/HolidaysEnjoyMonth.js",
        "/%(context)s/static/rh/ferias/reports/HolidaysActivity.js",
        "/%(context)s/static/rh/ferias/reports/HolidayEnjoyed.js",
        "/%(context)s/static/rh/ferias/holidayScale/HolidayScaleReportManager.js",
        "/%(context)s/static/rh/ferias/reports/HolidayStock.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    importlib.import_module("rh.ferias.signals.afastamento")
    importlib.import_module("rh.ferias.plugins.ferias_rh")
    importlib.import_module("rh.ferias.plugins.employee")
