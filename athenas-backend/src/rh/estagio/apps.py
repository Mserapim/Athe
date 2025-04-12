# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class GEPConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.estagio"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.estagio.views",
        # ESTAGIO PROBATORIO
        "rh.estagio.api.conceito",
        "rh.estagio.api.configuracao",
        "rh.estagio.api.comissaoavaliadora",
        "rh.estagio.api.integrantescomissao",
        "rh.estagio.api.estagioprobatorioservidor",
        "rh.estagio.api.estagioprobatorioavaliador",
        "rh.estagio.api.estagioprobatorioavaliado",
        "rh.estagio.api.estagioavaliacao",
        "rh.estagio.api.estagiocomissaoservidor",
        "rh.estagio.api.decisaoestagio",
        "rh.estagio.api.estagioprobatoriomembros",
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

    Application.register_stylesheet("/%(context)s/static/rh/images/gep/gep.css")
    Application.register_stylesheet("/%(context)s/static/rh/images/gep/estagio.css")

    js_paths = (
        "/%(context)s/static/rh/js/gep/gep.apreciacoes.js",
        "/%(context)s/static/rh/js/gep/gep.apreciacaocomissao.js",
        "/%(context)s/static/rh/js/gep/gep.apreciacaogestororgao.js",
        "/%(context)s/static/rh/js/gep/gep.configuradoravaliacao.js",
        "/%(context)s/static/rh/js/gep/gep.configuradorcomissao.js",
        "/%(context)s/static/rh/js/gep/gep.comissao.js",
        "/%(context)s/static/rh/js/gep/gep.comissaoform.js",
        "/%(context)s/static/rh/js/gep/gep.decisaogestorForm.js",
        "/%(context)s/static/rh/js/gep/gep.fatoravaliacao.js",
        "/%(context)s/static/rh/js/gep/gep.fatoravaliacaoForm.js",
        "/%(context)s/static/rh/js/gep/gep.gestorestagio.js",
        "/%(context)s/static/rh/js/gep/gep.gestoradmin.js",
        "/%(context)s/static/rh/js/gep/gep.integrantescomissao.js",
        "/%(context)s/static/rh/js/gep/gep.integrantecomissaoForm.js",
        "/%(context)s/static/rh/js/gep/gep.medias.js",
        "/%(context)s/static/rh/js/gep/gep.quesitoavaliacao.js",
        "/%(context)s/static/rh/js/gep/gep.quesitoavaliacaoForm.js",
        "/%(context)s/static/rh/js/gep/gep_questionario.js",
        "/%(context)s/static/rh/js/gep/gep.reportForm.js",
        "/%(context)s/static/rh/js/gep/gep.servidor.js",
        "/%(context)s/static/rh/js/gep/gep.notificacao.js",
        "/%(context)s/static/rh/js/gep/gep.NotaComissao.js",
        "/%(context)s/static/rh/estagio/conceito/ConceitoRestful.js",
        "/%(context)s/static/rh/estagio/conceito/ConceitoWindow.js",
        "/%(context)s/static/rh/estagio/conceito/ConceitoGrid.js",
        "/%(context)s/static/rh/estagio/configuracao/ConfiguracaoRestful.js",
        "/%(context)s/static/rh/estagio/configuracao/ConfiguracaoWindow.js",
        "/%(context)s/static/rh/estagio/configuracao/ConfiguracaoGrid.js",
        "/%(context)s/static/rh/estagio/configuracao/Manage.js",
        "/%(context)s/static/rh/estagio/comissao/ComissaoAvaliadoraRestful.js",
        "/%(context)s/static/rh/estagio/comissao/ComissaoAvaliadoraWindow.js",
        "/%(context)s/static/rh/estagio/comissao/ComissaoAvaliadoraGrid.js",
        "/%(context)s/static/rh/estagio/comissao/IntegrantesComissaoRestful.js",
        "/%(context)s/static/rh/estagio/comissao/IntegrantesComissaoWindow.js",
        "/%(context)s/static/rh/estagio/comissao/IntegrantesComissaoGrid.js",
        "/%(context)s/static/rh/estagio/comissao/Manage.js",
        "/%(context)s/static/rh/estagio/gestor/EstagioProbatorioServidorRestful.js",
        "/%(context)s/static/rh/estagio/gestor/EstagioProbatorioServidorWindow.js",
        "/%(context)s/static/rh/estagio/gestor/EstagioProbatorioServidorGrid.js",
        "/%(context)s/static/rh/estagio/gestor/Manage.js",
        "/%(context)s/static/rh/estagio/gestor/NotificacaoWindow.js",
        "/%(context)s/static/rh/estagio/gestor/RelatorioWindow.js",
        "/%(context)s/static/rh/estagio/gestor/NotaComissaoWindow.js",
        "/%(context)s/static/rh/estagio/gestor/InformacaoWindow.js",
        "/%(context)s/static/rh/estagio/gestor/HomologacaoWindow.js",
        "/%(context)s/static/rh/estagio/avaliador/EstagioProbatorioAvaliadorRestful.js",
        "/%(context)s/static/rh/estagio/avaliador/EstagioProbatorioAvaliadorWindow.js",
        "/%(context)s/static/rh/estagio/avaliador/EstagioProbatorioAvaliadorExternoWindow.js",
        "/%(context)s/static/rh/estagio/avaliador/EstagioProbatorioAvaliadorGrid.js",
        "/%(context)s/static/rh/estagio/avaliador/Manage.js",
        "/%(context)s/static/rh/estagio/avaliado/EstagioAvaliacaoRestful.js",
        "/%(context)s/static/rh/estagio/avaliado/EstagioAvaliacaoWindow.js",
        "/%(context)s/static/rh/estagio/avaliado/EstagioAvaliacaoGrid.js",
        "/%(context)s/static/rh/estagio/avaliado/Manage.js",
        "/%(context)s/static/rh/estagio/members_probationary_phase/EstagioAvaliacaoRestful.js",
        "/%(context)s/static/rh/estagio/members_probationary_phase/EstagioAvaliacaoWindow.js",
        "/%(context)s/static/rh/estagio/members_probationary_phase/EstagioAvaliacaoGrid.js",
        "/%(context)s/static/rh/estagio/members_probationary_phase/Manage.js",
        "/%(context)s/static/rh/estagio/members_probationary_phase/afastamentos/Restful.js",
        "/%(context)s/static/rh/estagio/members_probationary_phase/afastamentos/Grid.js",
        "/%(context)s/static/rh/estagio/members_probationary_phase/afastamentos/Manage.js",
        "/%(context)s/static/rh/estagio/comissaoavaliacao/EstagioComissaoServidorRestful.js",
        "/%(context)s/static/rh/estagio/comissaoavaliacao/EstagioComissaoServidorWindow.js",
        "/%(context)s/static/rh/estagio/comissaoavaliacao/EstagioComissaoServidorGrid.js",
        "/%(context)s/static/rh/estagio/comissaoavaliacao/Manage.js",
        "/%(context)s/static/rh/estagio/decisaoestagio/DecisaoEstagioRestful.js",
        "/%(context)s/static/rh/estagio/decisaoestagio/DecisaoEstagioWindow.js",
        "/%(context)s/static/rh/estagio/decisaoestagio/DecisaoEstagioWindowForm.js",
        "/%(context)s/static/rh/estagio/decisaoestagio/DecisaoEstagioGrid.js",
        "/%(context)s/static/rh/estagio/decisaoestagio/Manage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    importlib.import_module("rh.estagio.receivers")
