"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib

from django.apps import AppConfig


class SstConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "health.sst"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "health.sst.api.bodypart",
        "health.sst.api.causeragent",
        "health.sst.api.causeragentaccident",
        "health.sst.api.injury",
        "health.sst.api.workaccidentcommunication",
        "health.sst.api.monitoroccupationalhealth",
        "health.sst.api.examsst",
        "health.sst.api.environmentharmfulagent",
        "health.sst.api.environmentworkingcondition",
        "health.sst.api.epi",
        "health.sst.api.exposureemployeeenvironment",
        "health.sst.api.harmfulagent",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        # carregar qualquer outra coisa necessária ao app


def loaders():
    pass


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
        "/%(context)s/static/health/sst/BodyPartGrid.js",
        "/%(context)s/static/health/sst/BodyPartRestful.js",
        "/%(context)s/static/health/sst/BodyPartWindow.js",
        "/%(context)s/static/health/sst/BodyPartManage.js",
        "/%(context)s/static/health/sst/CauserAgentAccidentGrid.js",
        "/%(context)s/static/health/sst/CauserAgentAccidentRestful.js",
        "/%(context)s/static/health/sst/CauserAgentAccidentWindow.js",
        "/%(context)s/static/health/sst/CauserAgentAccidentManage.js",
        "/%(context)s/static/health/sst/CauserAgentGrid.js",
        "/%(context)s/static/health/sst/CauserAgentRestful.js",
        "/%(context)s/static/health/sst/CauserAgentWindow.js",
        "/%(context)s/static/health/sst/CauserAgentManage.js",
        "/%(context)s/static/health/sst/InjuryGrid.js",
        "/%(context)s/static/health/sst/InjuryRestful.js",
        "/%(context)s/static/health/sst/InjuryWindow.js",
        "/%(context)s/static/health/sst/InjuryManage.js",
        "/%(context)s/static/health/sst/WorkAccidentCommunicationGrid.js",
        "/%(context)s/static/health/sst/WorkAccidentCommunicationRestful.js",
        "/%(context)s/static/health/sst/WorkAccidentCommunicationWindow.js",
        "/%(context)s/static/health/sst/WorkAccidentCommunicationManage.js",
        "/%(context)s/static/health/sst/ExamSstGrid.js",
        "/%(context)s/static/health/sst/ExamSstRestful.js",
        "/%(context)s/static/health/sst/ExamSstWindow.js",
        "/%(context)s/static/health/sst/ExamSstManage.js",
        "/%(context)s/static/health/sst/MonitorOccupationalHealthGrid.js",
        "/%(context)s/static/health/sst/MonitorOccupationalHealthRestful.js",
        "/%(context)s/static/health/sst/MonitorOccupationalHealthWindow.js",
        "/%(context)s/static/health/sst/MonitorOccupationalHealthManage.js",
        "/%(context)s/static/health/sst/MonitoringHealthManage.js",
        "/%(context)s/static/health/sst/EpiGrid.js",
        "/%(context)s/static/health/sst/EpiRestful.js",
        "/%(context)s/static/health/sst/EpiWindow.js",
        "/%(context)s/static/health/sst/EpiManage.js",
        "/%(context)s/static/health/sst/HarmfulAgentGrid.js",
        "/%(context)s/static/health/sst/HarmfulAgentRestful.js",
        "/%(context)s/static/health/sst/HarmfulAgentWindow.js",
        "/%(context)s/static/health/sst/HarmfulAgentManage.js",
        "/%(context)s/static/health/sst/EnvironmentWorkingConditionGrid.js",
        "/%(context)s/static/health/sst/EnvironmentWorkingConditionRestful.js",
        "/%(context)s/static/health/sst/EnvironmentWorkingConditionWindow.js",
        "/%(context)s/static/health/sst/EnvironmentWorkingConditionManage.js",
        "/%(context)s/static/health/sst/EnvironmentHarmfulAgentGrid.js",
        "/%(context)s/static/health/sst/EnvironmentHarmfulAgentRestful.js",
        "/%(context)s/static/health/sst/EnvironmentHarmfulAgentWindow.js",
        "/%(context)s/static/health/sst/EnvironmentHarmfulAgentManage.js",
        "/%(context)s/static/health/sst/ExposureEmployeeEnvironmentGrid.js",
        "/%(context)s/static/health/sst/ExposureEmployeeEnvironmentRestful.js",
        "/%(context)s/static/health/sst/ExposureEmployeeEnvironmentWindow.js",
        "/%(context)s/static/health/sst/ExposureEmployeeEnvironmentManage.js",
        "/%(context)s/static/health/sst/WorkingConditionHarmfulAgentManage.js",
        "/%(context)s/static/health/sst/WorkingConditionExposureEmployeeManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="health")
