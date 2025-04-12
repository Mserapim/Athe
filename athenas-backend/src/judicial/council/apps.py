# -*- coding:utf-8 -*-

import importlib
from django.apps import AppConfig


class CouncilConfig(AppConfig):
    name = "judicial.council"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "judicial.council.api.distributionrapporteur",
        "judicial.council.api.convocationnotice",
        "judicial.council.api.councillor",
        "judicial.council.api.rapporteurdocument",
        "judicial.council.api.colegialdecision",
        "judicial.council.api.switchexecutionorgan",
        "judicial.council.api.voteattached",
        "judicial.council.api.vote",
        "judicial.council.api.devolutionrecommendation",
        "judicial.council.api.session",
        "judicial.council.api.sessionitem",
    ]

    def ready(self):
        register_statics()
        connect_signals()


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("judicial.council.signals.publication")


def register_statics():
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/judicial/council/council.css")

    js_paths = (
        "/%(context)s/static/judicial/council/session/SessionRestful.js",
        "/%(context)s/static/judicial/council/session/SessionWindow.js",
        "/%(context)s/static/judicial/council/session/SessionGrid.js",
        "/%(context)s/static/judicial/council/session/SessionItemRestful.js",
        "/%(context)s/static/judicial/council/session/SessionItemWindow.js",
        "/%(context)s/static/judicial/council/session/SessionItemGrid.js",
        "/%(context)s/static/judicial/council/session/Manage.js",
        "/%(context)s/static/judicial/council/DistributionRapporteurRestful.js",
        "/%(context)s/static/judicial/council/DistributionRapporteurWindow.js",
        "/%(context)s/static/judicial/council/DistributionRapporteurGrid.js",
        "/%(context)s/static/judicial/council/ConvocationNoticeRestful.js",
        "/%(context)s/static/judicial/council/ConvocationNoticeWindow.js",
        "/%(context)s/static/judicial/council/ConvocationNoticeGrid.js",
        "/%(context)s/static/judicial/council/CouncillorRestful.js",
        "/%(context)s/static/judicial/council/CouncillorWindow.js",
        "/%(context)s/static/judicial/council/CouncillorGrid.js",
        "/%(context)s/static/judicial/council/RapporteurDocumentRestful.js",
        "/%(context)s/static/judicial/council/RapporteurDocumentWindow.js",
        "/%(context)s/static/judicial/council/RapporteurDocumentGrid.js",
        "/%(context)s/static/judicial/council/DevolutionRecommendationRestful.js",
        "/%(context)s/static/judicial/council/DevolutionRecommendationWindow.js",
        "/%(context)s/static/judicial/council/DevolutionRecommendationGrid.js",
        "/%(context)s/static/judicial/council/ColegialDecisionRestful.js",
        "/%(context)s/static/judicial/council/ColegialDecisionWindow.js",
        "/%(context)s/static/judicial/council/ColegialDecisionGrid.js",
        "/%(context)s/static/judicial/council/VoteRestful.js",
        "/%(context)s/static/judicial/council/VoteWindow.js",
        "/%(context)s/static/judicial/council/VoteGrid.js",
        "/%(context)s/static/judicial/council/VoteAttachedRestful.js",
        "/%(context)s/static/judicial/council/VoteAttachedWindow.js",
        "/%(context)s/static/judicial/council/VoteAttachedGrid.js",
        "/%(context)s/static/judicial/council/SwitchExecutionOrganRestful.js",
        "/%(context)s/static/judicial/council/SwitchExecutionOrganWindow.js",
        "/%(context)s/static/judicial/council/SwitchExecutionOrganGrid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="judicial")
