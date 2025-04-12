# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class CIRDIRConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "corregedoria.cirdir"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "corregedoria.cirdir.api.controlinformation",
        "corregedoria.cirdir.api.employee",
        "corregedoria.cirdir.api.history",
        "corregedoria.cirdir.api.address",
        "corregedoria.cirdir.api.teaching",
        "corregedoria.cirdir.api.property",
        "corregedoria.cirdir.api.debits",
        "corregedoria.cirdir.api.discipline",
        "corregedoria.cirdir.api.institution",
        "corregedoria.cirdir.api.schedule",
        "corregedoria.cirdir.api.irscode",
        "corregedoria.cirdir.api.health",
        "corregedoria.cirdir.api.privatelog",
        "corregedoria.cirdir.api.healtharea",
        "corregedoria.cirdir.api.evaluator",
        "corregedoria.cirdir.api.healthareaevaluation",
        "corregedoria.cirdir.api.healthassessment",
        "corregedoria.cirdir.api.managementhealtharea",
        "corregedoria.cirdir.api.report",
        "corregedoria.cirdir.api.irpf",
        "corregedoria.cirdir.api.informationevaluation",
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
    importlib.import_module("corregedoria.cirdir.notify")


def connect_signals():
    importlib.import_module("corregedoria.cirdir.signals.check_proviment")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/corregedoria/cirdir/ActionsMixin.js",
        "/%(context)s/static/corregedoria/cirdir/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/Manage.js",
        "/%(context)s/static/corregedoria/cirdir/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/Window.js",
        "/%(context)s/static/corregedoria/cirdir/EmployeeRestful.js",
        "/%(context)s/static/corregedoria/cirdir/EmployeeGrid.js",
        "/%(context)s/static/corregedoria/cirdir/AddYearWindow.js",
        "/%(context)s/static/corregedoria/cirdir/AddEmployeeWindow.js",
        "/%(context)s/static/corregedoria/cirdir/DeleteWindow.js",
        "/%(context)s/static/corregedoria/cirdir/OpenWindow.js",
        "/%(context)s/static/corregedoria/cirdir/CloseWindow.js",
        "/%(context)s/static/corregedoria/cirdir/ScheduleActionsWindow.js",
        "/%(context)s/static/corregedoria/cirdir/HistoryWindow.js",
        "/%(context)s/static/corregedoria/cirdir/history/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/history/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/history/Window.js",
        "/%(context)s/static/corregedoria/cirdir/address/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/address/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/address/Window.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/Window.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/discipline/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/discipline/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/discipline/Window.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/discipline/ManageWindow.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/institution/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/institution/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/institution/Window.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/institution/ManageWindow.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/schedule/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/schedule/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/schedule/Window.js",
        "/%(context)s/static/corregedoria/cirdir/teaching/schedule/ManageWindow.js",
        "/%(context)s/static/corregedoria/cirdir/irscode/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/irscode/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/irscode/Window.js",
        "/%(context)s/static/corregedoria/cirdir/property/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/property/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/property/Window.js",
        "/%(context)s/static/corregedoria/cirdir/debits/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/debits/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/debits/Window.js",
        "/%(context)s/static/corregedoria/cirdir/irpf/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/irpf/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/irpf/Window.js",
        "/%(context)s/static/corregedoria/cirdir/health/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/health/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/health/Window.js",
        "/%(context)s/static/corregedoria/cirdir/PrivateLogWindow.js",
        "/%(context)s/static/corregedoria/cirdir/privatelog/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/privatelog/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/privatelog/Window.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/Manage.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/SendSearch.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/IndicateEvaluator.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/ManagementHealthArea.js",
        "/%(context)s/static/corregedoria/cirdir/evaluator/Manage.js",
        "/%(context)s/static/corregedoria/cirdir/evaluator/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/evaluator/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/evaluator/Window.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/attendance/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/attendance/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/health/healtharea/attendance/Manage.js",
        "/%(context)s/static/corregedoria/cirdir/health/assessment/Manage.js",
        "/%(context)s/static/corregedoria/cirdir/health/assessment/Grid.js",
        "/%(context)s/static/corregedoria/cirdir/health/assessment/Restful.js",
        "/%(context)s/static/corregedoria/cirdir/health/assessment/Window.js",
        "/%(context)s/static/corregedoria/cirdir/health/assessment/PendenceManagementWindow.js",
        "/%(context)s/static/corregedoria/cirdir/report/BaseWindow.js",
        "/%(context)s/static/corregedoria/cirdir/report/TeachingReport.js",
        "/%(context)s/static/corregedoria/cirdir/report/TestReport.js",
        "/%(context)s/static/corregedoria/cirdir/report/EmployeePendenceReport.js",
        "/%(context)s/static/corregedoria/cirdir/report/EmployeeMemberPendenceReport.js",
        "/%(context)s/static/corregedoria/cirdir/report/SubmittedAfterDeadlineReport.js",
        "/%(context)s/static/corregedoria/cirdir/report/MemberPendenceListReport.js",
        "/%(context)s/static/corregedoria/cirdir/report/MemberListAddressReport.js",
        "/%(context)s/static/corregedoria/cirdir/AuditManage.js",
        "/%(context)s/static/corregedoria/cirdir/InformationEvaluationGrid.js",
        "/%(context)s/static/corregedoria/cirdir/InformationEvaluationRestful.js",
        "/%(context)s/static/corregedoria/cirdir/InformationEvaluationWindow.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="corregedoria")
