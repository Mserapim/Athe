# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class RafConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "raf"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "raf.api.activity",
        "raf.api.activityadjustment",
        "raf.api.autoreference",
        "raf.api.configuration",
        "raf.api.conversation",
        "raf.api.employee",
        "raf.api.functionalactivityreport",
        "raf.api.item",
        "raf.api.subitem",
        "raf.api.subitemcalculate",
        "raf.api.quiz",
        "raf.api.taxonomyclassification",
        "raf.api.trustrelationship",
        "raf.api.typequiz",
        "raf.api.util",
        "raf.api.workerlocation",
        "raf.api.yearbase",
        "raf.api.nonproceduralactivities",
        "raf.api.searchprocessnumber",
        "raf.api.dataadjustment",
        "raf.api.legalclass",
        "raf.api.legalmatter",
        "raf.api.legalmovement",
        "raf.api.management",
        "raf.api.specialorgan",
        "raf.api.solicitation",
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
    importlib.import_module("raf.notify")


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

    Application.register_stylesheet("/%(context)s/static/raf/raf.css")

    js_paths = (
        "/%(context)s/static/raf/Configuration.js",
        "/%(context)s/static/raf/yearbase/Restful.js",
        "/%(context)s/static/raf/yearbase/Window.js",
        "/%(context)s/static/raf/yearbase/Grid.js",
        "/%(context)s/static/raf/typequiz/Restful.js",
        "/%(context)s/static/raf/typequiz/Window.js",
        "/%(context)s/static/raf/typequiz/Grid.js",
        "/%(context)s/static/raf/functionalactivityreport/Restful.js",
        "/%(context)s/static/raf/functionalactivityreport/Window.js",
        "/%(context)s/static/raf/functionalactivityreport/Grid.js",
        "/%(context)s/static/raf/functionalactivityreport/GroupGrid.js",
        "/%(context)s/static/raf/functionalactivityreport/Launcher.js",
        "/%(context)s/static/raf/functionalactivityreport/ChangeEmployeeWindow.js",
        "/%(context)s/static/raf/functionalactivityreport/FollowAdjustmentWindow.js",
        "/%(context)s/static/raf/functionalactivityreport/HistoricRAFWindow.js",
        "/%(context)s/static/raf/workerlocation/Restful.js",
        "/%(context)s/static/raf/workerlocation/Window.js",
        "/%(context)s/static/raf/workerlocation/Grid.js",
        "/%(context)s/static/raf/quiz/Restful.js",
        "/%(context)s/static/raf/quiz/Window.js",
        "/%(context)s/static/raf/quiz/Grid.js",
        "/%(context)s/static/raf/quiz/Launcher.js",
        "/%(context)s/static/raf/quiz/FilterBaseWindow.js",
        "/%(context)s/static/raf/quiz/YearFilterWindow.js",
        "/%(context)s/static/raf/quiz/CopyQuizWindow.js",
        "/%(context)s/static/raf/item/Restful.js",
        "/%(context)s/static/raf/item/Window.js",
        "/%(context)s/static/raf/item/Grid.js",
        "/%(context)s/static/raf/subitem/Restful.js",
        "/%(context)s/static/raf/subitem/Window.js",
        "/%(context)s/static/raf/subitem/Grid.js",
        "/%(context)s/static/raf/subitem/CalculateRestful.js",
        "/%(context)s/static/raf/subitem/CalculateWindow.js",
        "/%(context)s/static/raf/subitem/CalculateGrid.js",
        "/%(context)s/static/raf/activity/Restful.js",
        "/%(context)s/static/raf/activity/Window.js",
        "/%(context)s/static/raf/activity/Grid.js",
        "/%(context)s/static/raf/activity/Launcher.js",
        "/%(context)s/static/raf/activity/AllActivitieswindow.js",
        "/%(context)s/static/raf/trustrelationship/Restful.js",
        "/%(context)s/static/raf/trustrelationship/Launcher.js",
        "/%(context)s/static/raf/trustrelationship/Grid.js",
        "/%(context)s/static/raf/trustrelationship/Window.js",
        "/%(context)s/static/raf/FillActivityGrid.js",
        "/%(context)s/static/raf/FillActivityWindow.js",
        "/%(context)s/static/raf/FillAdjustmentWindow.js",
        "/%(context)s/static/raf/ViewTaxonomyWindow.js",
        "/%(context)s/static/raf/taxonomyclassification/Restful.js",
        "/%(context)s/static/raf/taxonomyclassification/Grid.js",
        "/%(context)s/static/raf/taxonomyclassification/Window.js",
        "/%(context)s/static/rh/employee/Restful.js",
        "/%(context)s/static/rh/employee/Grid.js",
        "/%(context)s/static/raf/EmployeeRestful.js",
        "/%(context)s/static/raf/EmployeeGrid.js",
        "/%(context)s/static/raf/report/BaseWindow.js",
        "/%(context)s/static/raf/report/ExtractReportPeriodWindow.js",
        "/%(context)s/static/raf/report/ProductivityReportPeriodWindow.js",
        "/%(context)s/static/raf/report/ExtractAdjustmentWindow.js",
        "/%(context)s/static/raf/report/ExtractReportPeriodStatusRAF.js",
        "/%(context)s/static/raf/report/StatisticRAFReport.js",
        "/%(context)s/static/raf/report/ExtractReportLocationPeriodWindow.js",
        "/%(context)s/static/raf/autoreference/Restful.js",
        "/%(context)s/static/raf/autoreference/Grid.js",
        "/%(context)s/static/raf/autoreference/Window.js",
        "/%(context)s/static/raf/autoreference/DetailWindow.js",
        "/%(context)s/static/raf/autoreference/InfoAutoReferenceWindow.js",
        "/%(context)s/static/raf/autoreference/InfoAutoReferenceWindow.js",
        "/%(context)s/static/raf/autoreference/AttendanceWindow.js",
        "/%(context)s/static/raf/autoreference/DataEprocWindow.js",
        "/%(context)s/static/raf/autoreference/DataEExtWindow.js",
        "/%(context)s/static/raf/autoreference/DataAdjustmentWindow.js",
        "/%(context)s/static/raf/conversation/Restful.js",
        "/%(context)s/static/raf/conversation/AnswerWindow.js",
        "/%(context)s/static/raf/management/GroupGrid.js",
        "/%(context)s/static/raf/management/ManagementRAF.js",
        "/%(context)s/static/raf/management/CreateRAFWindow.js",
        "/%(context)s/static/raf/management/DropRAFWindow.js",
        "/%(context)s/static/raf/management/ImportEproc2AthenasWindow.js",
        "/%(context)s/static/raf/management/DropEproc2AthenasWindow.js",
        "/%(context)s/static/raf/management/ImportEExt2AthenasWindow.js",
        "/%(context)s/static/raf/management/DropEExt2AthenasWindow.js",
        "/%(context)s/static/raf/management/AddWorkerlocationWindow.js",
        "/%(context)s/static/raf/management/DelWorkerlocationWindow.js",
        "/%(context)s/static/raf/management/DefineDate.js",
        "/%(context)s/static/raf/management/SendEdocWindow.js",
        "/%(context)s/static/raf/adjustment/BaseGrid.js",
        "/%(context)s/static/raf/adjustment/BaseRestful.js",
        "/%(context)s/static/raf/adjustment/BaseWindow.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/Restful.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/Grid.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/Window.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/RejectWindow.js",
        "/%(context)s/static/raf/adjustment/AdjustmentEmployeeGrid.js",
        "/%(context)s/static/raf/adjustment/AdjustmentEmployeeWindow.js",
        "/%(context)s/static/raf/adjustment/AdjustmentEmployeeRestful.js",
        "/%(context)s/static/raf/adjustment/AdjustmentInternalControlRestful.js",
        "/%(context)s/static/raf/adjustment/AdjustmentInternalControlGrid.js",
        "/%(context)s/static/raf/adjustment/AdjustmentInternalControlWindow.js",
        "/%(context)s/static/raf/adjustment/AdjustmentAnalysisInternalControlWindow.js",
        "/%(context)s/static/raf/adjustment/RejectAdjustmentWindow.js",
        "/%(context)s/static/raf/adjustment/UndoActionAdjustmentWindow.js",
        "/%(context)s/static/raf/adjustment/AdjustmentInternalControlManage.js",
        "/%(context)s/static/raf/FillAdjustmentManageWindow.js",
        "/%(context)s/static/raf/nonproceduralactivities/Restful.js",
        "/%(context)s/static/raf/nonproceduralactivities/Window.js",
        "/%(context)s/static/raf/nonproceduralactivities/Grid.js",
        "/%(context)s/static/raf/nonproceduralactivities/Manage.js",
        "/%(context)s/static/raf/searchprocessnumber/SearchProcessNumberWindow.js",
        "/%(context)s/static/raf/searchprocessnumber/Grid.js",
        "/%(context)s/static/raf/searchprocessnumber/Restful.js",
        "/%(context)s/static/raf/searchprocessnumber/Window.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/LegalClassRestful.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/LegalClassGrid.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/LegalMatterRestful.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/LegalMatterGrid.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/LegalMovementRestful.js",
        "/%(context)s/static/raf/adjustment/dataadjustment/LegalMovementGrid.js",
        "/%(context)s/static/raf/specialorgan/Grid.js",
        "/%(context)s/static/raf/specialorgan/Restful.js",
        "/%(context)s/static/raf/specialorgan/Window.js",
        "/%(context)s/static/raf/solicitation/Grid.js",
        "/%(context)s/static/raf/solicitation/Restful.js",
        "/%(context)s/static/raf/solicitation/Window.js",
        "/%(context)s/static/raf/solicitation/Manage.js",
        "/%(context)s/static/raf/management/Launcher.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="raf")
