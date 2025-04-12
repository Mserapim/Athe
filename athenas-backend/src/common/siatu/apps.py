# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class SiatuConfig(AppConfig):
    name = "common.siatu"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "common.siatu.api",
    ]

    def ready(self):
        register_statics()
        # connect_signals()
        # carregar qualquer outra coisa necessária ao app
        importlib.import_module("common.siatu.loader")


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/common/siatu/siatu.css")
    Application.register_stylesheet("/%(context)s/static/common/siatu/siatu128.css")

    js_paths = (
        "/%(context)s/static/common/siatu/core.js",
        "/%(context)s/static/common/siatu/chamado/Restful.js",
        # '/%(context)s/static/edocs/protocolo/SelectProtocolWindow.js',
        "/%(context)s/static/common/siatu/chamado/ItemBaseConhecimento/Restful.js",
        "/%(context)s/static/common/siatu/chamado/ItemBaseConhecimento/Window.js",
        "/%(context)s/static/common/siatu/chamado/ItemBaseConhecimento/Grid.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/modelo/Restful.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/modelo/Window.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/modelo/Grid.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/modelo/Manager.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/objeto/Restful.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/objeto/Window.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/objeto/Grid.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/objeto/Manager.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/Restful.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/Window.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/Grid.js",
        "/%(context)s/static/common/siatu/BaseConhecimento/Manager.js",
        "/%(context)s/static/common/siatu/configuration/email/Restful.js",
        "/%(context)s/static/common/siatu/configuration/email/Panel.js",
        "/%(context)s/static/common/siatu/configuration/email/Manager.js",
        "/%(context)s/static/common/siatu/configuration/distribuicao/Restful.js",
        "/%(context)s/static/common/siatu/configuration/distribuicao/Panel.js",
        "/%(context)s/static/common/siatu/configuration/distribuicao/Manager.js",
        "/%(context)s/static/common/siatu/atendente/Restful.js",
        "/%(context)s/static/common/siatu/atendente/WindowNotificacao.js",
        "/%(context)s/static/common/siatu/atendente/Window.js",
        "/%(context)s/static/common/siatu/atendente/Grid.js",
        "/%(context)s/static/common/siatu/atendente/Manager.js",
        "/%(context)s/static/common/siatu/terceiro/Restful.js",
        "/%(context)s/static/common/siatu/terceiro/Window.js",
        "/%(context)s/static/common/siatu/terceiro/Grid.js",
        "/%(context)s/static/common/siatu/terceiro/Manager.js",
        "/%(context)s/static/common/siatu/terceirizada/Restful.js",
        "/%(context)s/static/common/siatu/terceirizada/Window.js",
        "/%(context)s/static/common/siatu/terceirizada/Grid.js",
        "/%(context)s/static/common/siatu/terceirizada/Manager.js",
        "/%(context)s/static/common/siatu/gerente/Restful.js",
        "/%(context)s/static/common/siatu/gerente/Window.js",
        "/%(context)s/static/common/siatu/gerente/Grid.js",
        "/%(context)s/static/common/siatu/gerente/Manager.js",
        "/%(context)s/static/common/siatu/servico/AtendentesRestful.js",
        "/%(context)s/static/common/siatu/servico/AtendentesWindow.js",
        "/%(context)s/static/common/siatu/servico/AtendentesGrid.js",
        "/%(context)s/static/common/siatu/servico/Restful.js",
        "/%(context)s/static/common/siatu/servico/Window.js",
        "/%(context)s/static/common/siatu/servico/Tree.js",
        "/%(context)s/static/common/siatu/servico/Manager.js",
        "/%(context)s/static/common/siatu/servico/ManagerGerente.js",
        "/%(context)s/static/common/siatu/solicitacao/Restful.js",
        "/%(context)s/static/common/siatu/solicitacao/WindowGerente.js",
        "/%(context)s/static/common/siatu/solicitacao/WindowSolicitante.js",
        "/%(context)s/static/common/siatu/chamado/urgente/Window.js",
        "/%(context)s/static/common/siatu/chamado/avaliacao/Restful.js",
        "/%(context)s/static/common/siatu/chamado/avaliacao/Window.js",
        "/%(context)s/static/common/siatu/chamado/avaliacao/WindowReplica.js",
        "/%(context)s/static/common/siatu/chamado/avaliacao/NeutralizarWindow.js",
        "/%(context)s/static/common/siatu/chamado/reincidencia/Restful.js",
        "/%(context)s/static/common/siatu/chamado/reincidencia/WindowGerente.js",
        "/%(context)s/static/common/siatu/chamado/reincidencia/WindowAtendente.js",
        "/%(context)s/static/common/siatu/chamado/status/Restful.js",
        "/%(context)s/static/common/siatu/chamado/status/concluirWindow.js",
        "/%(context)s/static/common/siatu/chamado/status/Window.js",
        "/%(context)s/static/common/siatu/chamado/status/Grid.js",
        "/%(context)s/static/common/siatu/chamado/transferencia/PanelGerentes.js",
        "/%(context)s/static/common/siatu/chamado/transferencia/Restful.js",
        "/%(context)s/static/common/siatu/chamado/transferencia/Window.js",
        "/%(context)s/static/common/siatu/chamado/transferencia/WindowDecidir.js",
        "/%(context)s/static/common/siatu/chamado/transferencia/Grid.js",
        "/%(context)s/static/common/siatu/chamado/anexo/Restful.js",
        "/%(context)s/static/common/siatu/chamado/anexo/Window.js",
        "/%(context)s/static/common/siatu/chamado/anexo/Grid.js",
        "/%(context)s/static/common/siatu/chamado/WindowCancelar.js",
        "/%(context)s/static/common/siatu/chamado/WindowDistribuir.js",
        "/%(context)s/static/common/siatu/chamado/Window.js",
        "/%(context)s/static/common/siatu/chamado/Grid.js",
        "/%(context)s/static/common/siatu/chamado/AtendenteGrid.js",
        "/%(context)s/static/common/siatu/chamado/TabInfoSolicitante.js",
        "/%(context)s/static/common/siatu/chamado/TabPrincipal.js",
        "/%(context)s/static/common/siatu/chamado/TabTransferencia.js",
        "/%(context)s/static/common/siatu/chamado/TabDistribuicaoManual.js",
        "/%(context)s/static/common/siatu/chamado/TabCfgEmailAtendente.js",
        "/%(context)s/static/common/siatu/chamado/TabCfgEmailSolicitante.js",
        "/%(context)s/static/common/siatu/chamado/TabTerceiroInterno.js",
        "/%(context)s/static/common/siatu/chamado/TabAnexo.js",
        "/%(context)s/static/common/siatu/chamado/ManagerTransfExterna.js",
        "/%(context)s/static/common/siatu/chamado/Manager.js",
        "/%(context)s/static/common/siatu/chamado/ManagerSolicitante.js",
        "/%(context)s/static/common/siatu/chamado/ManagerAtendente.js",
        "/%(context)s/static/common/siatu/chamado/ManagerGerente.js",
        "/%(context)s/static/common/siatu/reports/BaseManager.js",
        "/%(context)s/static/common/siatu/reports/AttendanceDescriptionManager.js",
        "/%(context)s/static/common/siatu/reports/NumberOfAttendancesPerAttendantManager.js",
        "/%(context)s/static/common/siatu/reports/AttendanceAvaliationConceptManager.js",
        "/%(context)s/static/common/siatu/reports/AttendanceAvaliationGraphicsManager.js",
        "/%(context)s/static/common/siatu/ConfigurationManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
