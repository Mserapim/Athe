# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django import apps


class AppConfig(
    apps.AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.pvf"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "rh.pvf.api.pvfrequest.portalrequest",
        "rh.pvf.api.pvfrequest.portalrequestusufruct",
        "rh.pvf.api.pvfrequest.portalrequesthistory",
        "rh.pvf.api.pvfmyrights.myrights",
        "rh.pvf.api.pvfrequest.portalrequestworkload",
        "rh.pvf.api.pvfrequest.portalrequestsubstitute",
        "rh.pvf.api.pvfrequest.portalcancelschedule",
        "rh.pvf.api.pvfrequest.portalretificationschedule",
        "rh.pvf.api.usufructs.usufruct",
        "rh.pvf.api.pvfcalendar.pvfcalendar",
        "rh.pvf.api.pvfcalendar",
        "rh.pvf.api.employee.employee",
        "rh.pvf.api.paycheck",
        "rh.pvf.api.pointsheet.pointsheet",
        "rh.pvf.api.pointsheet.sendpointsheet",
        "rh.pvf.api.pointsheet.pointjustification",
        "rh.pvf.api.telework.marktelework",
        "rh.pvf.api.telework.sendtelework",
        "rh.pvf.api.shiftmanager",
        "rh.pvf.api.progression.request_progression",
    ]

    def ready(self):
        connect_signals()
        # load_notify()
        register_statics()


def connect_signals():
    #     importlib.import_module('rh.pvf.signals.departure')
    importlib.import_module("rh.pvf.signals")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:
        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/rh/pvf/portalrequest/Restful.js",
        "/%(context)s/static/rh/pvf/portalrequest/Window.js",
        "/%(context)s/static/rh/pvf/portalrequest/DetailWindow.js",
        "/%(context)s/static/rh/pvf/portalrequest/Grid.js",
        "/%(context)s/static/rh/pvf/portalrequest/Manage.js",
        "/%(context)s/static/rh/pvf/portalrequestusufruct/Restful.js",
        "/%(context)s/static/rh/pvf/portalrequestusufruct/Window.js",
        "/%(context)s/static/rh/pvf/portalrequestusufruct/DetailWindow.js",
        "/%(context)s/static/rh/pvf/portalrequestusufruct/RectifyWindow.js",
        "/%(context)s/static/rh/pvf/portalrequestusufruct/Grid.js",
        "/%(context)s/static/rh/pvf/portalrequestusufruct/Manage.js",
        "/%(context)s/static/rh/pvf/waitingapproval/Restful.js",
        "/%(context)s/static/rh/pvf/waitingapproval/Window.js",
        "/%(context)s/static/rh/pvf/waitingapproval/DetailWindow.js",
        "/%(context)s/static/rh/pvf/waitingapproval/DeferAndDenyWindow.js",
        "/%(context)s/static/rh/pvf/waitingapproval/Grid.js",
        "/%(context)s/static/rh/pvf/waitingapproval/Manage.js",
        "/%(context)s/static/rh/pvf/portalrequesthistory/Restful.js",
        "/%(context)s/static/rh/pvf/portalrequesthistory/Window.js",
        "/%(context)s/static/rh/pvf/portalrequesthistory/DetailWindow.js",
        "/%(context)s/static/rh/pvf/portalrequesthistory/Grid.js",
        "/%(context)s/static/rh/pvf/portalrequesthistory/Manage.js",
        "/%(context)s/static/rh/pvf/myrights/Manage.js",
        "/%(context)s/static/rh/pvf/myrights/RightTypeGrid.js",
        "/%(context)s/static/rh/pvf/myrights/RightTypeRestful.js",
        "/%(context)s/static/rh/pvf/myrights/AcquisitionPeriodGrid.js",
        "/%(context)s/static/rh/pvf/myrights/AcquisitionPeriodRestful.js",
        "/%(context)s/static/rh/pvf/myrights/UsufructGrid.js",
        "/%(context)s/static/rh/pvf/myrights/UsufructRestful.js",
        "/%(context)s/static/rh/pvf/myrights/AttachmentWindow.js",
        "/%(context)s/static/rh/pvf/portalrequestworkload/Restful.js",
        "/%(context)s/static/rh/pvf/portalrequestworkload/Window.js",
        "/%(context)s/static/rh/pvf/portalrequestworkload/DetailWindow.js",
        "/%(context)s/static/rh/pvf/portalrequestworkload/Grid.js",
        "/%(context)s/static/rh/pvf/portalrequestworkload/Manage.js",
        "/%(context)s/static/rh/pvf/portalrequestsubstitute/Restful.js",
        "/%(context)s/static/rh/pvf/portalrequestsubstitute/Window.js",
        "/%(context)s/static/rh/pvf/portalrequestsubstitute/Grid.js",
        "/%(context)s/static/rh/pvf/portalrequestsubstitute/Manage.js",
        "/%(context)s/static/rh/pvf/portalcancelschedule/Restful.js",
        "/%(context)s/static/rh/pvf/portalcancelschedule/Window.js",
        "/%(context)s/static/rh/pvf/portalcancelschedule/DetailWindow.js",
        "/%(context)s/static/rh/pvf/portalcancelschedule/Grid.js",
        "/%(context)s/static/rh/pvf/portalcancelschedule/Manage.js",
        "/%(context)s/static/rh/pvf/portalretificationschedule/Restful.js",
        "/%(context)s/static/rh/pvf/portalretificationschedule/Window.js",
        "/%(context)s/static/rh/pvf/portalretificationschedule/DetailWindow.js",
        "/%(context)s/static/rh/pvf/portalretificationschedule/Grid.js",
        "/%(context)s/static/rh/pvf/portalretificationschedule/Manage.js",
        "/%(context)s/static/rh/pvf/portalusufruct/Restful.js",
        "/%(context)s/static/rh/pvf/portalusufruct/Window.js",
        "/%(context)s/static/rh/pvf/portalusufruct/Grid.js",
        "/%(context)s/static/rh/pvf/portalusufruct/Manage.js",
        "/%(context)s/static/rh/pvf/portalusufructretification/Restful.js",
        "/%(context)s/static/rh/pvf/portalusufructretification/Grid.js",
        "/%(context)s/static/rh/pvf/portalusufructretification/Window.js",
        "/%(context)s/static/rh/pvf/portalusufructretification/Manage.js",
        "/%(context)s/static/rh/pvf/employee/Restful.js",
        "/%(context)s/static/rh/pvf/employee/Window.js",
        "/%(context)s/static/rh/pvf/employee/Grid.js",
        "/%(context)s/static/rh/pvf/employee/Manage.js",
        "/%(context)s/static/rh/pvf/reports/PayCheckManage.js",
        "/%(context)s/static/rh/pvf/reports/Calendar.js",
        "/%(context)s/static/rh/pvf/reports/CalendarForm.js",
        "/%(context)s/static/rh/pvf/reports/PointSheet.js",
        "/%(context)s/static/rh/pvf/reports/PointSheetReport.js",
        "/%(context)s/static/rh/pvf/reports/ShiftControlReport.js",
        "/%(context)s/static/rh/pvf/reports/NegativeBalancePoint.js",
        "/%(context)s/static/rh/pvf/reports/AppoverVdfReport.js",
        "/%(context)s/static/rh/pvf/progression/Restful.js",
        "/%(context)s/static/rh/pvf/progression/Window.js",
        "/%(context)s/static/rh/pvf/progression/Manage.js",
        "/%(context)s/static/rh/pvf/progression/DetailWindow.js",
        "/%(context)s/static/rh/pvf/progression_h/Restful.js",
        "/%(context)s/static/rh/pvf/progression_h/Window.js",
        "/%(context)s/static/rh/pvf/progression_h/Manage.js",
        "/%(context)s/static/rh/pvf/progression_h/DetailWindow.js",
        "/%(context)s/static/rh/pvf/progression_h/document/Restful.js",
        "/%(context)s/static/rh/pvf/progression_h/document/Window.js",
        "/%(context)s/static/rh/pvf/progression_h/document/Manage.js",
        "/%(context)s/static/rh/pvf/progression_h/document/Grid.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/Restful.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/Window.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/Manage.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/RegisterPoint.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/PointJustificationRestful.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/PointJustificationGrid.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/PointJustificationWindow.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/PointJustificationManage.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/DetailWindow.js",
        "/%(context)s/static/rh/pvf/sendpointsheet/ReferenceWindow.js",
        "/%(context)s/static/rh/pvf/sendtelework/Restful.js",
        "/%(context)s/static/rh/pvf/sendtelework/Window.js",
        "/%(context)s/static/rh/pvf/sendtelework/Manage.js",
        "/%(context)s/static/rh/pvf/sendtelework/MarkTeleworkRestful.js",
        "/%(context)s/static/rh/pvf/sendtelework/MarkTeleworkGrid.js",
        "/%(context)s/static/rh/pvf/sendtelework/MarkTeleworkWindow.js",
        "/%(context)s/static/rh/pvf/sendtelework/MarkTeleworkManage.js",
        "/%(context)s/static/rh/pvf/sendtelework/DetailWindow.js",
        "/%(context)s/static/rh/pvf/shiftmanager/Restful.js",
        "/%(context)s/static/rh/pvf/shiftmanager/Window.js",
        "/%(context)s/static/rh/pvf/shiftmanager/Grid.js",
        "/%(context)s/static/rh/pvf/shiftmanager/Manage.js",
        "/%(context)s/static/rh/pvf/shiftmanager/DetailWindow.js",
        "/%(context)s/static/rh/pvf/shiftmanager/RestfulResume.js",
        "/%(context)s/static/rh/pvf/shiftmanager/WindowResume.js",
        "/%(context)s/static/rh/pvf/shiftmanager/GridResume.js",
        "/%(context)s/static/rh/pvf/shiftmanager/ManageResume.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")
