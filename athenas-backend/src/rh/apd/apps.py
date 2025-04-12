# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class APDConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.apd"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        # APD - AVALIACAO PERIODICA DE DESEMPENHO
        "rh.apd.api.configuration",
        "rh.apd.api.commission",
        "rh.apd.api.membercommission",
        "rh.apd.api.periodicevaluationperformance",
        "rh.apd.api.evaluation",
        "rh.apd.api.manifestation",
        "rh.apd.api.resource",
        "rh.apd.api.scoreevaluation",
        "rh.apd.api.homologation",
        "rh.apd.api.decisioncommission",
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
    importlib.import_module("rh.apd.receivers")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/rh/apd/apd.css")

    js_paths = (
        "/%(context)s/static/rh/apd/configuration/ConfigurationRestful.js",
        "/%(context)s/static/rh/apd/configuration/ConfigurationWindow.js",
        "/%(context)s/static/rh/apd/configuration/ConfigurationGrid.js",
        "/%(context)s/static/rh/apd/configuration/Manage.js",
        "/%(context)s/static/rh/apd/commission/CommissionRestful.js",
        "/%(context)s/static/rh/apd/commission/CommissionWindow.js",
        "/%(context)s/static/rh/apd/commission/CommissionGrid.js",
        "/%(context)s/static/rh/apd/membercommission/MemberCommissionRestful.js",
        "/%(context)s/static/rh/apd/membercommission/MemberCommissionWindow.js",
        "/%(context)s/static/rh/apd/membercommission/MemberCommissionGrid.js",
        "/%(context)s/static/rh/apd/commission/Manage.js",
        "/%(context)s/static/rh/apd/periodicevaluationperformance/PeriodicEvaluationPerformanceRestful.js",
        "/%(context)s/static/rh/apd/periodicevaluationperformance/PeriodicEvaluationPerformanceWindow.js",
        "/%(context)s/static/rh/apd/periodicevaluationperformance/ExternalEvaluationWindow.js",
        "/%(context)s/static/rh/apd/periodicevaluationperformance/RepeatLastManualEvaluation.js",
        "/%(context)s/static/rh/apd/periodicevaluationperformance/TextReconsiderationWindow.js",
        "/%(context)s/static/rh/apd/periodicevaluationperformance/PeriodicEvaluationPerformanceGrid.js",
        "/%(context)s/static/rh/apd/periodicevaluationperformance/Manage.js",
        "/%(context)s/static/rh/apd/evaluation/EvaluationRestful.js",
        "/%(context)s/static/rh/apd/evaluation/EvaluationWindow.js",
        "/%(context)s/static/rh/apd/evaluation/OpinionReconsiderationWindow.js",
        "/%(context)s/static/rh/apd/evaluation/EvaluationGrid.js",
        "/%(context)s/static/rh/apd/evaluation/Manage.js",
        "/%(context)s/static/rh/apd/manifestation/ManifestationRestful.js",
        "/%(context)s/static/rh/apd/manifestation/ManifestationWindow.js",
        "/%(context)s/static/rh/apd/manifestation/RequestResourceWindow.js",
        "/%(context)s/static/rh/apd/manifestation/ReconsiderationWindow.js",
        "/%(context)s/static/rh/apd/manifestation/ManifestationGrid.js",
        "/%(context)s/static/rh/apd/manifestation/Manage.js",
        "/%(context)s/static/rh/apd/resource/ResourceRestful.js",
        "/%(context)s/static/rh/apd/resource/ResourceWindow.js",
        "/%(context)s/static/rh/apd/resource/ResourceGrid.js",
        "/%(context)s/static/rh/apd/resource/Manage.js",
        "/%(context)s/static/rh/apd/scoreevaluation/ScoreEvaluationRestful.js",
        "/%(context)s/static/rh/apd/scoreevaluation/ScoreEvaluationWindow.js",
        "/%(context)s/static/rh/apd/scoreevaluation/ScoreEvaluationGrid.js",
        # '/%(context)s/static/rh/apd/scoreevaluation/Manage.js',
        "/%(context)s/static/rh/apd/homologation/HomologationRestful.js",
        "/%(context)s/static/rh/apd/homologation/HomologationWindow.js",
        "/%(context)s/static/rh/apd/homologation/MultiWindow.js",
        "/%(context)s/static/rh/apd/homologation/HomologationGrid.js",
        "/%(context)s/static/rh/apd/homologation/Manage.js",
        "/%(context)s/static/rh/apd/decisioncommission/DecisionCommissionRestful.js",
        "/%(context)s/static/rh/apd/decisioncommission/DecisionCommissionWindow.js",
        "/%(context)s/static/rh/apd/decisioncommission/DecisionCommissionGrid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")
