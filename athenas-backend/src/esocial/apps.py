# -*- coding:utf-8 -*-


"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


# Substituir "Sample" pelo nome que preferir dar ao AppConfig
class EsocialConfig(AppConfig):
    name = "esocial"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "esocial.api.manager",
        "esocial.api.configuration",
        "esocial.api.qualification",
        "esocial.api.occurrence",
        "esocial.api.returnresult",
        "esocial.api.itemtable",
        "esocial.api.payrollperiod",
        "esocial.api.pendencyperiod",
        "esocial.generators.qualification.reports",
        "esocial.tasks.generation",
        "esocial.tasks.qualification",
        "esocial.tasks.tasks",
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
    importlib.import_module("esocial.signals.rh_models")
    importlib.import_module("esocial.signals.event")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/esocial/esocial.css")

    js_paths = (
        "/%(context)s/static/esocial/configuration/ConfigurationRestful.js",
        "/%(context)s/static/esocial/configuration/ConfigurationWindow.js",
        "/%(context)s/static/esocial/configuration/ConfigurationCertificateWindow.js",
        "/%(context)s/static/esocial/configuration/ConfigurationGrid.js",
        "/%(context)s/static/esocial/configuration/ConfigurationManage.js",
        "/%(context)s/static/esocial/manager/MenuMaintenanceItem.js",
        "/%(context)s/static/esocial/manager/MenuGeneratePayrollWindow.js",
        "/%(context)s/static/esocial/manager/MenuSelecionarCategoriaWindow.js",
        "/%(context)s/static/esocial/manager/EventUpdateWindow.js",
        "/%(context)s/static/esocial/manager/PeriodFilterAction.js",
        "/%(context)s/static/esocial/manager/EventRestful.js",
        "/%(context)s/static/esocial/manager/EventWindow.js",
        "/%(context)s/static/esocial/manager/EventGrid.js",
        "/%(context)s/static/esocial/manager/EventDetailRestful.js",
        "/%(context)s/static/esocial/manager/EventDetailGrid.js",
        "/%(context)s/static/esocial/manager/Manage.js",
        "/%(context)s/static/esocial/manager/ManageEmployee.js",
        "/%(context)s/static/esocial/manager/EventSummaryRestful.js",
        "/%(context)s/static/esocial/manager/EventSummaryGrid.js",
        "/%(context)s/static/esocial/manager/EventSummaryWindow.js",
        "/%(context)s/static/esocial/manager/BatchEventRestful.js",
        "/%(context)s/static/esocial/manager/BatchEventWindow.js",
        "/%(context)s/static/esocial/manager/BatchEventGrid.js",
        "/%(context)s/static/esocial/occurrence/Restful.js",
        "/%(context)s/static/esocial/occurrence/Window.js",
        "/%(context)s/static/esocial/occurrence/Grid.js",
        "/%(context)s/static/esocial/occurrence/Manage.js",
        "/%(context)s/static/esocial/returnresult/Restful.js",
        "/%(context)s/static/esocial/returnresult/Window.js",
        "/%(context)s/static/esocial/returnresult/Grid.js",
        "/%(context)s/static/esocial/returnresult/Manage.js",
        "/%(context)s/static/esocial/itemtable/ItemRestful.js",
        "/%(context)s/static/esocial/itemtable/ItemWindow.js",
        "/%(context)s/static/esocial/itemtable/ItemGrid.js",
        "/%(context)s/static/esocial/itemtable/Manage.js",
        "/%(context)s/static/esocial/manager/xml/WindowShow.js",
        "/%(context)s/static/esocial/manager/OccurrenceWindow.js",
        "/%(context)s/static/esocial/manager/DependencyWindow.js",
        "/%(context)s/static/esocial/qualification/RegistrationQualificationManage.js",
        "/%(context)s/static/esocial/qualification/RegistrationQualificationRestful.js",
        "/%(context)s/static/esocial/qualification/RegistrationQualificationWindow.js",
        "/%(context)s/static/esocial/qualification/RegistrationQualificationGrid.js",
        "/%(context)s/static/esocial/dependency/DependencyRestful.js",
        "/%(context)s/static/esocial/dependency/DependencyWindow.js",
        "/%(context)s/static/esocial/dependency/DependencyGrid.js",
        "/%(context)s/static/esocial/payrollperiod/Manage.js",
        "/%(context)s/static/esocial/payrollperiod/Restful.js",
        "/%(context)s/static/esocial/payrollperiod/Window.js",
        "/%(context)s/static/esocial/payrollperiod/Grid.js",
        "/%(context)s/static/esocial/payrollperiod/PendencyPeriodManage.js",
        "/%(context)s/static/esocial/payrollperiod/PendencyPeriodRestful.js",
        "/%(context)s/static/esocial/payrollperiod/PendencyPeriodWindow.js",
        "/%(context)s/static/esocial/payrollperiod/PendencyPeriodGrid.js",
        "/%(context)s/static/esocial/payrollperiod/PayrollPeriodManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="esocial")


def loaders():
    pass
