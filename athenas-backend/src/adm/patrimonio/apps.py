# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib

from django.apps import AppConfig


# Substituir "Sample" pelo nome que preferir dar ao AppConfig
class PatrimonioConfig(AppConfig):
    name = "adm.patrimonio"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        # patrimonio
        "adm.patrimonio.api.conta",
        "adm.patrimonio.api.baixa",
        "adm.patrimonio.api.especie",
        "adm.patrimonio.api.grupoespecie",
        "adm.patrimonio.api.sequencia",
        "adm.patrimonio.api.manage",
        "adm.patrimonio.api.entrada",
        "adm.patrimonio.api.incorporacao",
        "adm.patrimonio.api.localizacao",
        "adm.patrimonio.api.movimento",
        "adm.patrimonio.api.documento",
        "adm.patrimonio.api.avaliacao",
        "adm.patrimonio.api.suspensao",
        "adm.patrimonio.api.reports",
        "adm.patrimonio.api.criticarnotaentrada",
        "adm.patrimonio.api.grupocontabil",
        "adm.patrimonio.api.notification",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()

        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass
    # Patrimonio
    importlib.import_module("adm.patrimonio.signals.message")
    importlib.import_module("adm.patrimonio.signals.historico")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/adm/patrimonio/patrimonio.css")

    js_paths = (
        "/%(context)s/static/adm/js/core.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoContabilRestful.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoContabilGrid.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoContabilWindow.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoEspecieRestful.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoEspecieGrid.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoEspecieWindow.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoEspecieMovimentacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/parametro/GrupoEspecieManage.js",
        "/%(context)s/static/adm/patrimonio/parametro/ContaRestful.js",
        "/%(context)s/static/adm/patrimonio/parametro/ContaGrid.js",
        "/%(context)s/static/adm/patrimonio/parametro/ContaWindow.js",
        "/%(context)s/static/adm/patrimonio/parametro/ContaManage.js",
        "/%(context)s/static/adm/patrimonio/parametro/SequenciaRestful.js",
        "/%(context)s/static/adm/patrimonio/parametro/SequenciaGrid.js",
        "/%(context)s/static/adm/patrimonio/parametro/SequenciaWindow.js",
        "/%(context)s/static/adm/patrimonio/parametro/SequenciaManage.js",
        "/%(context)s/static/adm/patrimonio/parametro/EspecieRestful.js",
        "/%(context)s/static/adm/patrimonio/parametro/EspecieWindow.js",
        "/%(context)s/static/adm/patrimonio/parametro/EspecieMovimentacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/parametro/EspecieGrid.js",
        "/%(context)s/static/adm/patrimonio/DocumentoRestful.js",
        "/%(context)s/static/adm/patrimonio/DocumentoRestfulWindow.js",
        "/%(context)s/static/adm/patrimonio/DocumentoGrid.js",
        "/%(context)s/static/adm/patrimonio/reports/BaseWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/AnaliticoAtivoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/AnaliticoAdquiridoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/AnaliticoBaixadoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/AnaliticoAvaliadoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/SinteticoAdquiridoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/SinteticoBaixadoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/SinteticoAtivoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/SinteticoAtivoLiquidoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/SinteticoAvaliadoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/ResumoAtivoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/ResumoAdquiridoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/ResumoBaixadoWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/CommonFields.js",
        "/%(context)s/static/adm/patrimonio/reports/GenericReportWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/ActiveAssetsWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/AcquiredAssetsWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/DepreciatedAssetsWindow.js",
        "/%(context)s/static/adm/patrimonio/reports/ActiveAssetsByLocationWindow.js",
        "/%(context)s/static/adm/patrimonio/PatrimonioRestful.js",
        "/%(context)s/static/adm/patrimonio/PatrimonioRestfulWindow.js",
        "/%(context)s/static/adm/patrimonio/ChangeConservationWindow.js",
        "/%(context)s/static/adm/patrimonio/PatrimonioGrid.js",
        "/%(context)s/static/adm/patrimonio/Manage.js",
        "/%(context)s/static/adm/patrimonio/SuspensaoRestful.js",
        "/%(context)s/static/adm/patrimonio/SuspensaoWindow.js",
        "/%(context)s/static/adm/patrimonio/SuspensaoGrid.js",
        "/%(context)s/static/adm/patrimonio/SuspensaoManage.js",
        "/%(context)s/static/adm/patrimonio/localizacao/Restful.js",
        "/%(context)s/static/adm/patrimonio/localizacao/Window.js",
        "/%(context)s/static/adm/patrimonio/localizacao/Grid.js",
        "/%(context)s/static/adm/patrimonio/localizacao/Tree.js",
        "/%(context)s/static/adm/patrimonio/localizacao/Manage.js",
        "/%(context)s/static/adm/patrimonio/localizacao/FilterWindow.js",
        "/%(context)s/static/adm/patrimonio/entrada/Restful.js",
        "/%(context)s/static/adm/patrimonio/entrada/Window.js",
        "/%(context)s/static/adm/patrimonio/entrada/Grid.js",
        "/%(context)s/static/adm/patrimonio/entrada/CriticarNotaEntradaRestful.js",
        "/%(context)s/static/adm/patrimonio/entrada/CriticarNotaEntradaWindow.js",
        "/%(context)s/static/adm/patrimonio/entrada/CriticarNotaEntradaGrid.js",
        "/%(context)s/static/adm/patrimonio/entrada/ItemEntradaRestful.js",
        "/%(context)s/static/adm/patrimonio/entrada/ItemEntradaWindow.js",
        "/%(context)s/static/adm/patrimonio/entrada/ItemEntradaGrid.js",
        "/%(context)s/static/adm/patrimonio/entrada/NotaFiscalRestful.js",
        "/%(context)s/static/adm/patrimonio/entrada/NotaFiscalWindow.js",
        "/%(context)s/static/adm/patrimonio/entrada/NotaConvenioRestful.js",
        "/%(context)s/static/adm/patrimonio/entrada/NotaConvenioWindow.js",
        "/%(context)s/static/adm/patrimonio/entrada/NotaDoacaoRestful.js",
        "/%(context)s/static/adm/patrimonio/entrada/NotaDoacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/entrada/Manage.js",
        "/%(context)s/static/adm/patrimonio/baixa/Restful.js",
        "/%(context)s/static/adm/patrimonio/baixa/Window.js",
        "/%(context)s/static/adm/patrimonio/baixa/Grid.js",
        "/%(context)s/static/adm/patrimonio/baixa/ItemBaixaRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/ItemBaixaWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/ItemBaixaGrid.js",
        "/%(context)s/static/adm/patrimonio/baixa/AlienacaoRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/AlienacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/DoacaoRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/DoacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/ExtravioRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/ExtravioWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/InservibilidadeRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/InservibilidadeWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/MudancaClassificacaoRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/MudancaClassificacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/SinistroRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/SinistroWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/TransferenciaRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/TransferenciaWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/AjusteInventarioRestful.js",
        "/%(context)s/static/adm/patrimonio/baixa/AjusteInventarioWindow.js",
        "/%(context)s/static/adm/patrimonio/baixa/Manage.js",
        "/%(context)s/static/adm/patrimonio/movimento/ItemRestful.js",
        "/%(context)s/static/adm/patrimonio/movimento/ItemWindow.js",
        "/%(context)s/static/adm/patrimonio/movimento/ItemGrid.js",
        "/%(context)s/static/adm/patrimonio/movimento/LogStatusRestful.js",
        "/%(context)s/static/adm/patrimonio/movimento/LogStatusWindow.js",
        "/%(context)s/static/adm/patrimonio/movimento/LogStatusGrid.js",
        "/%(context)s/static/adm/patrimonio/movimento/LogStatusManage.js",
        "/%(context)s/static/adm/patrimonio/movimento/Restful.js",
        "/%(context)s/static/adm/patrimonio/movimento/RestfulWindow.js",
        "/%(context)s/static/adm/patrimonio/movimento/Grid.js",
        "/%(context)s/static/adm/patrimonio/movimento/DetailMovimentItemWindow.js",
        "/%(context)s/static/adm/patrimonio/movimento/PanelManage.js",
        "/%(context)s/static/adm/patrimonio/movimento/TabManage.js",
        "/%(context)s/static/adm/patrimonio/movimento/WindowManage.js",
        "/%(context)s/static/adm/patrimonio/movimento/StatusManifestation.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/TabelaManage.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/TabelaRestful.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/TabelaWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/TabelaCopyWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/TabelaGrid.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ItemTabelaRestful.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ItemTabelaWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ItemTabelaGrid.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ParametroRestful.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ParametroWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ConservacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/VidaUtilWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/UtilizacaoWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ParametroGrid.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/Restful.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/Window.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/Grid.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ItemRestful.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ItemWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ManualItemWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/RevaluateItemWindow.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/ItemGrid.js",
        "/%(context)s/static/adm/patrimonio/avaliacao/Manage.js",
        "/%(context)s/static/adm/patrimonio/notification/Restful.js",
        "/%(context)s/static/adm/patrimonio/notification/Window.js",
        "/%(context)s/static/adm/patrimonio/notification/Grid.js",
        "/%(context)s/static/adm/patrimonio/core.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="adm")
