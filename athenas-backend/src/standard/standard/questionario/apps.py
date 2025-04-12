# -*- coding:utf-8 -*-

import importlib
from django.apps import AppConfig


class QuestionarioConfig(AppConfig):
    name = "standard.questionario"

    controllers = [
        "standard.questionario.views",
    ]

    def ready(self):
        register_statics()
        # connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/js/toolkit/questionario/GerenciaQuestionario.js",
        "/%(context)s/static/js/toolkit/questionario/QuestionarioGrid.js",
        "/%(context)s/static/js/toolkit/questionario/ElementoQuestionarioGrid.js",
        "/%(context)s/static/js/toolkit/questionario/AlternativaGrid.js",
        "/%(context)s/static/js/toolkit/questionario/QuestionarioForm.js",
        "/%(context)s/static/js/toolkit/questionario/ReferenciaTextualForm.js",
        "/%(context)s/static/js/toolkit/questionario/QuestaoForm.js",
        "/%(context)s/static/js/toolkit/questionario/QuestaoEnumForm.js",
        "/%(context)s/static/js/toolkit/questionario/QuestaoAbertaForm.js",
        "/%(context)s/static/js/toolkit/questionario/QuestaoMSForm.js",
        "/%(context)s/static/js/toolkit/questionario/QuestaoCertoErradoForm.js",
        "/%(context)s/static/js/toolkit/questionario/AlternativaForm.js",
        "/%(context)s/static/js/toolkit/questionario/MontaQuestionario.js",
        "/%(context)s/static/js/toolkit/questionario/VerResposta.js",
        "/%(context)s/static/js/toolkit/questionario/core.js",
    )

    Application.register_stylesheet("/%(context)s/static/css/questionario.css")

    for path in js_paths:
        Application.register_javascript(path, scope="standard")
