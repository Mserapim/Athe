# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class GratificationsManagerConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.gratifications_manager"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.gratifications_manager.api.cumulative_exercises",
        "rh.gratifications_manager.api.cumulative_exercises_permanent",
        "rh.gratifications_manager.api.aux_coordenation",
        "rh.gratifications_manager.api.diligence",
        "rh.gratifications_manager.api.gratifications",
        "rh.gratifications_manager.api.member_gratifications",
        "rh.gratifications_manager.api.cumulativo_substituicao",
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
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    # importlib.import_module('rh.gratifications_manager.signals')


def loaders():
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application
        '/%(context)s/static/web/js/shortcuts.js',

        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    js_paths = (
        # ORGANIZED LOADERS ----------------------------------------------------------------------------
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises/Window.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/Window.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/PayrollManage.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/PayrollGrid.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/PayrollRestful.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/PayrollWindow.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/substitutions/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/substitutions/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_consolidated/substitutions/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/periodo/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/periodo/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/periodo/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/periodo/Window.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/consolidado/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/consolidado/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/consolidado/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/consolidado/Window.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/designacoes/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/designacoes/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/cumulative_exercises_permanent/designacoes/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/diligence/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/diligence/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/diligence/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/diligence/Window.js",
        "/%(context)s/static/rh/gratifications_manager/diligence/gratificacao/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/diligence/gratificacao/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/diligence/gratificacao/Window.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/Window.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/workassignment/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/workassignment/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/workassignment/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/workassignment/Window.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/gratificacao/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/gratificacao/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/aux_coordenation/gratificacao/Window.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/ManagePanel.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/Window.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/WorkplaceGrid.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/EmployeeGrid.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/workassignment/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/workassignment/Window.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/workplace_tag/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/workplace_tag/Window.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/workplace_tag/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/gratifications/workplace_tag/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/periodo/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/periodo/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/periodo/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/periodo/Window.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/membros_consolidados/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/membros_consolidados/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/membros_consolidados/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/membros_consolidados/Window.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/gratificacoes/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/gratificacoes/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/gratificacoes/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/gratificacoes/Window.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/designacoes/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/designacoes/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/member_gratifications/designacoes/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/vendas_cumulativo_substituicao/Manage.js",
        "/%(context)s/static/rh/gratifications_manager/vendas_cumulativo_substituicao/Grid.js",
        "/%(context)s/static/rh/gratifications_manager/vendas_cumulativo_substituicao/Restful.js",
        "/%(context)s/static/rh/gratifications_manager/vendas_cumulativo_substituicao/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")

    # 'Registro dos Stylesheet's para este aplicativo'
    Application.register_stylesheet("/%(context)s/static/rh/images/fopag/fopag.css")
    Application.register_stylesheet("/%(context)s/static/rh/images/fopag/style.css")
    Application.register_stylesheet(
        "/%(context)s/static/rh/images/progressoes/sprite-progressoes.css"
    )
