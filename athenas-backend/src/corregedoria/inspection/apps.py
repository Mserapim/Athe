# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class InspectionConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "corregedoria.inspection"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "corregedoria.inspection.api.inspection",
        "corregedoria.inspection.api.registrationpublicattendance",
        "corregedoria.inspection.api.bookofregisteroutcourtlawsuitcontrol",
        "corregedoria.inspection.api.bookofregistercourtlawsuitcontrol",
        "corregedoria.inspection.api.registrationcourtlawsuitreceived",
        "corregedoria.inspection.api.registrationcourtlawsuitreturned",
        "corregedoria.inspection.api.registrationcourtlawsuitelectoralreceived",
        "corregedoria.inspection.api.registrationcourtlawsuitelectoralreturned",
        "corregedoria.inspection.api.processesforanalysisperformanceinaudiences",
        "corregedoria.inspection.api.personalmovement",
        "corregedoria.inspection.api.structureeffectiveemployees",
        "corregedoria.inspection.api.structurecommissionedemployees",
        "corregedoria.inspection.api.structureexternalemployees",
        "corregedoria.inspection.api.structureexternalpeoples",
        "corregedoria.inspection.api.procforqualanalysisofthepartscivilcourtlawsuit",
        "corregedoria.inspection.api.procforqualanalysisofthepartscriminalcourtlawsuit",
        "corregedoria.inspection.api.procforqualanalysisofthepartsoutcourtlawsuit",
        "corregedoria.inspection.api.procforqualanalysisofthepartselectoral",
        "corregedoria.inspection.api.recommendations",
        "corregedoria.inspection.api.attachments",
        "corregedoria.inspection.api.proceduralmovementreceived",
        "corregedoria.inspection.api.proceduralmovementreturned",
        "corregedoria.inspection.api.proceduralmovementoutcourtlawsuit",
        "corregedoria.inspection.api.procforqualanalysisofthepartsprocuratorate",
        "corregedoria.inspection.api.followrecommendation",
        "corregedoria.inspection.api.deadlinerecommendationattachments",
        "corregedoria.inspection.api.notificationhistory",
        "corregedoria.inspection.api.memberorgan",
        "corregedoria.inspection.api.structureequipment",
        "corregedoria.inspection.api.structuregeneralstatus",
        "corregedoria.inspection.api.administrativeorganizationoperatinghours",
        "corregedoria.inspection.api.existingregisters",
        "corregedoria.inspection.api.administrativeorganizationproceduresinprogress",
        "corregedoria.inspection.api.administrativeorganizationarchivedprocedures",
        "corregedoria.inspection.api.administrativeorganizationgeneralstatus",
        "corregedoria.inspection.api.performance",
        "corregedoria.inspection.api.report",
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
    importlib.import_module("corregedoria.inspection.notify")


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

    js_paths = (
        "/%(context)s/static/corregedoria/inspection/inspection/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/Manage.js",
        "/%(context)s/static/corregedoria/inspection/inspection/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/WindowExecutionOrgan.js",
        "/%(context)s/static/corregedoria/inspection/inspection/WindowAuxiliaryOrgan.js",
        "/%(context)s/static/corregedoria/inspection/inspection/WindowEspecialGroup.js",
        "/%(context)s/static/corregedoria/inspection/inspection/SendCommunicationCPJCSMP.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/Launcher_executionorgan_prosecution.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/Launcher_executionorgan_procuratorate.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/Launcher_auxiliaryorgan.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/Launcher_especialgroup.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationpublicattendance/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationpublicattendance/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationpublicattendance/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/bookofregisteroutcourtlawsuitcontrol/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/bookofregisteroutcourtlawsuitcontrol/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/bookofregisteroutcourtlawsuitcontrol/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/bookofregistercourtlawsuitcontrol/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/bookofregistercourtlawsuitcontrol/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/bookofregistercourtlawsuitcontrol/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitreceived/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitreceived/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitreceived/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitreturned/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitreturned/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitreturned/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitelectoralreceived/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitelectoralreceived/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitelectoralreceived/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitelectoralreturned/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitelectoralreturned/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/registrationcourtlawsuitelectoralreturned/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/processesforanalysisperformanceinaudiences/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/processesforanalysisperformanceinaudiences/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/regularityofservices/processesforanalysisperformanceinaudiences/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/BaseGrid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/BaseRestful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/EffetiveGrid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/EffetiveRestful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/CommissionedGrid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/CommissionedRestful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/ExternalGrid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/ExternalRestful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/ExternalPeoplesGrid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/personalmovement/ExternalPeoplesRestful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureeffectiveemployees/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureeffectiveemployees/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureeffectiveemployees/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structurecommissionedemployees/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structurecommissionedemployees/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structurecommissionedemployees/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureexternalemployees/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureexternalemployees/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureexternalemployees/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureexternalpeoples/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureexternalpeoples/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/structure/structureexternalpeoples/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartscivilcourtlawsuit/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartscivilcourtlawsuit/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartscivilcourtlawsuit/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartscriminalcourtlawsuit/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartscriminalcourtlawsuit/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartscriminalcourtlawsuit/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartsoutcourtlawsuit/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartsoutcourtlawsuit/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartsoutcourtlawsuit/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartselectoral/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartselectoral/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/functionalperformance/procforqualanalysisofthepartselectoral/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/generaldata/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/generaldata/memberorgan/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/generaldata/memberorgan/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/generaldata/memberorgan/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/operatingstructure/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/operatingstructure/structureequipment/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/operatingstructure/structureequipment/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/operatingstructure/structureequipment/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/existingregisters/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/existingregisters/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/existingregisters/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/proceduresinprogress/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/proceduresinprogress/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/proceduresinprogress/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/archivedprocedures/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/archivedprocedures/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/administrativeorganization/archivedprocedures/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/performance/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/generalobservations/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/recommendations/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/recommendations/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/recommendations/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/recommendations/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/recommendations/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/attachments/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/attachments/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/attachments/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/attachments/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/sign/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementreceived/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementreceived/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementreceived/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementreturned/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementreturned/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementreturned/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementoutcourtlawsuit/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementoutcourtlawsuit/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/proceduralmovementoutcourtlawsuit/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/procforqualanalysisofthepartsprocuratorate/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/procforqualanalysisofthepartsprocuratorate/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/procforqualanalysisofthepartsprocuratorate/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/filling/procuratorate/Launcher.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/Manage.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/DelayOfTimeWindow.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/ReportComplianceWindow.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/attachments/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/attachments/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/follow_recommendation/attachments/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/Manage.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/AnalyzeWindow.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/attachments/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/attachments/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/attachments/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/notificationhistory/Grid.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/notificationhistory/Restful.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/notificationhistory/Window.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/notificationhistory/Manage.js",
        "/%(context)s/static/corregedoria/inspection/inspection/report/HistoryInspectionReport.js",
        "/%(context)s/static/corregedoria/inspection/inspection/analyze_recommendation/NotifyPersonalized.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="corregedoria")
