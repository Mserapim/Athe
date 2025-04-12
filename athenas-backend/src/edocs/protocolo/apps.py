# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
import pathlib

from django.apps import AppConfig
from django.conf import settings


class ProtocoloConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "edocs.protocolo"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "edocs.protocolo.views",
        "edocs.protocolo.api.tipodocumento",
        "edocs.protocolo.api.manage",
        "edocs.protocolo.api.anexo",
        "edocs.protocolo.api.attachment",
        "edocs.protocolo.api.protocolo",
        "edocs.protocolo.api.referencia",
        "edocs.protocolo.api.groupperson",
        "edocs.protocolo.api.groupgeneralorgan",
        "edocs.protocolo.api.impressora",
        "edocs.protocolo.rpc.main",
        "edocs.protocolo.rpc.online_protocol",
        "edocs.protocolo.rpc.online_certificate",
        "edocs.protocolo.rpc.plid_protocol",
        "edocs.protocolo.rpc.lgpd_protocol",
        "edocs.protocolo.api.masterboxprotocol",
        "edocs.protocolo.api.movement",
        "edocs.protocolo.api.flowchart",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        sync()
        mkdir()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    importlib.import_module("edocs.protocolo.signals.distributiontable")
    importlib.import_module("edocs.protocolo.signals.custom")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/edocs/protocolo/edocs.css")
    Application.register_stylesheet("/%(context)s/static/edocs/protocolo/protocolo.css")

    js_paths = (
        "/%(context)s/static/edocs/js/core.js",
        "/%(context)s/static/edocs/js/protocolo.js",
        "/%(context)s/static/edocs/reports/AthenasReport.js",
        "/%(context)s/static/edocs/reports/DocumentTransferGuide.js",
        "/%(context)s/static/edocs/reports/IncomingMovementReport.js",
        "/%(context)s/static/edocs/reports/OutcomingMovementReport.js",
        "/%(context)s/static/edocs/reports/Flowchart.js",
        "/%(context)s/static/edocs/reports/ReportTermConfidentiality.js",
        "/%(context)s/static/edocs/protocolo/core.js",
        "/%(context)s/static/edocs/protocolo/TipoDocumentoRestful.js",
        "/%(context)s/static/edocs/protocolo/TipoDocumentoWindow.js",
        "/%(context)s/static/edocs/protocolo/TipoDocumentoGrid.js",
        "/%(context)s/static/edocs/protocolo/TipoDocumentoManage.js",
        "/%(context)s/static/edocs/protocolo/ProtocoloRestful.js",
        "/%(context)s/static/edocs/protocolo/ProtocoloWindow.js",
        "/%(context)s/static/edocs/protocolo/ProtocoloGrid.js",
        "/%(context)s/static/edocs/protocolo/AttachmentRestful.js",
        "/%(context)s/static/edocs/protocolo/AttachmentWindow.js",
        "/%(context)s/static/edocs/protocolo/AttachmentGrid.js",
        "/%(context)s/static/edocs/protocolo/ProtocolReferenceDetailWindow.js",
        "/%(context)s/static/edocs/protocolo/ReferenciaRestful.js",
        "/%(context)s/static/edocs/protocolo/ReferenciaWindow.js",
        "/%(context)s/static/edocs/protocolo/ReferenciaGrid.js",
        "/%(context)s/static/edocs/protocolo/ReferenciaManage.js",
        "/%(context)s/static/edocs/protocolo/ImpressoraRestful.js",
        "/%(context)s/static/edocs/protocolo/ImpressoraWindow.js",
        "/%(context)s/static/edocs/protocolo/ImpressoraGrid.js",
        "/%(context)s/static/edocs/protocolo/ImpressoraManage.js",
        "/%(context)s/static/edocs/protocolo/GroupPersonRestful.js",
        "/%(context)s/static/edocs/protocolo/GroupPersonWindow.js",
        "/%(context)s/static/edocs/protocolo/GroupPersonGrid.js",
        "/%(context)s/static/edocs/protocolo/GroupPersonManage.js",
        "/%(context)s/static/edocs/protocolo/GroupGeneralOrganRestful.js",
        "/%(context)s/static/edocs/protocolo/GroupGeneralOrganWindow.js",
        "/%(context)s/static/edocs/protocolo/GroupGeneralOrganGrid.js",
        "/%(context)s/static/edocs/protocolo/GroupGeneralOrganManage.js",
        "/%(context)s/static/edocs/protocolo/SelectLocationWindow.js",
        "/%(context)s/static/edocs/protocolo/box/MixinSelectionGrid.js",
        "/%(context)s/static/edocs/protocolo/box/PersonDestinationGrid.js",
        "/%(context)s/static/edocs/protocolo/box/LocationDestinationGrid.js",
        "/%(context)s/static/edocs/protocolo/box/GroupPersonDestinationGrid.js",
        "/%(context)s/static/edocs/protocolo/box/GroupLocationDestinationGrid.js",
        "/%(context)s/static/edocs/protocolo/box/Grid.js",
        "/%(context)s/static/edocs/protocolo/box/ComposeWindow.js",
        "/%(context)s/static/edocs/protocolo/box/ComposeExWindow.js",
        "/%(context)s/static/edocs/protocolo/box/ComposeMovementWindow.js",
        "/%(context)s/static/edocs/protocolo/box/ComposeFinalizeWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/FilterMixin.js",
        "/%(context)s/static/edocs/protocolo/filters/FilterWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/InterestedWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/SendedByWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/OriginWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/DestinationWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/SendDateWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/SpecieWindow.js",
        "/%(context)s/static/edocs/protocolo/filters/DepartmentWindow.js",
        "/%(context)s/static/edocs/protocolo/box/MainGrid.js",
        "/%(context)s/static/edocs/protocolo/box/PersonGrid.js",
        "/%(context)s/static/edocs/protocolo/box/HistoryGrid.js",
        "/%(context)s/static/edocs/protocolo/box/ClosedGrid.js",
        "/%(context)s/static/edocs/protocolo/box/SharedGrid.js",
        "/%(context)s/static/edocs/protocolo/Manage.js",
        "/%(context)s/static/edocs/protocolo/SelectProtocolWindow.js",
        "/%(context)s/static/edocs/protocolo/masterbox/Manage.js",
        "/%(context)s/static/edocs/protocolo/masterbox/Restful.js",
        "/%(context)s/static/edocs/protocolo/masterbox/Grid.js",
        "/%(context)s/static/edocs/protocolo/masterbox/Window.js",
        "/%(context)s/static/edocs/protocolo/tasks/EdocDetail.js",
        "/%(context)s/static/edocs/protocolo/movement/Restful.js",
        "/%(context)s/static/edocs/protocolo/movement/Window.js",
        "/%(context)s/static/edocs/protocolo/movement/Grid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="edocs")


def loaders():
    importlib.import_module("edocs.protocolo.loader")


def sync():
    importlib.import_module("edocs.protocolo.dasync")


def mkdir():
    # Cria diretório de cache, se não existir, para armazenar
    # arquivos de fluxogramas de protocolos.
    flowchart_cache_dir = getattr(settings, "CACHE", {}).get("flowchart", None)
    if flowchart_cache_dir:
        pathlib.Path(flowchart_cache_dir).mkdir(parents=True, exist_ok=True)
