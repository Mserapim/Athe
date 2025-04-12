from django.urls import path, include
from reports.apiv2.views.reportbaseviews import (
    ConsultaSituacaoRelatorio,
    PVFDownloadJasperFile,
    ReportDownloadFile,
)
from reports.apiv2.views.pvf.gestao_pvf import GestaoVDFReportView
from reports.apiv2.views.pvf.reportviews import (
    PVFRelatorioFolhaPontoView,
    PVFFichaFinanceiraView,
    PVFInformeRendimentoView,
    PVFPayCheckView,
    PVFRelatorioAprovadoresView,
    PVFReportAnotacaoPessoalView,
    PVFReportCalendarView,
    PVFReportDeliveryTimeSheet,
    PVFReportEmployeeScaleView,
    PVFReportPointSheetView,
    PVFReportTeleWorkView,
    ReportContraChequeview,
)

from reports.apiv2.views.ceaf.reportviews import CapacitacaoRelatorioView
from reports.apiv2.views.gfp.ficha_financeira import FichaFinanceiraRelatorioView
from reports.apiv2.views.anotacao_pessoal.anotacao.anotacao_pessoal import (
    AnotacaoPessoalRelatorioView,
)

from reports.apiv2.views.diarias.os_consolidada import OsConsolidadaDiariasView
from reports.apiv2.views.diarias.prestacao_contas import PrestacaoContasDiariasView


urlpatterns = [
    # pvf
    path(
        "rh/pvf/employee-scale/",
        PVFReportEmployeeScaleView.as_view(),
        name="employee-scale",
    ),
    path("rh/pvf/paycheck/", ReportContraChequeview.as_view(), name="paycheck"),
    path("rh/pvf/point-sheet/", PVFReportPointSheetView.as_view(), name="point-sheet"),
    path("rh/pvf/telework/", PVFReportTeleWorkView.as_view(), name="telework"),
    path("rh/pvf/calendar/", PVFReportCalendarView.as_view(), name="calendar"),
    path(
        "rh/pvf/delivery-point-sheet/",
        PVFReportDeliveryTimeSheet.as_view(),
        name="delivery-point-sheet",
    ),
    path(
        "rh/pvf/approvers/",
        PVFRelatorioAprovadoresView.as_view(),
        name="relatorio_aprovadores",
    ),
    path(
        "rh/pvf/financial-statement/",
        PVFFichaFinanceiraView.as_view(),
        name="relatorio_ficha_financeira",
    ),
    path(
        "rh/pvf/income-statement/",
        PVFInformeRendimentoView.as_view(),
        name="relatorio_informe_rendimentos",
    ),
    path(
        "rh/pvf/anotacao-pessoal/",
        PVFReportAnotacaoPessoalView.as_view(),
        name="relatorio_anotacao_pessoal",
    ),
    path(
        "rh/pvf/folha-ponto/",
        PVFRelatorioFolhaPontoView.as_view(),
        name="relatorio_folha_ponto",
    ),
    # VDF
    path(
        "rh/gestao/vdf/",
        GestaoVDFReportView.as_view(),
        name="gestao-vdf-relatorio",
    ),
    # Ceaf
    path(
        "ceaf/capacitacao/",
        CapacitacaoRelatorioView.as_view(),
        name="ceaf-relatorio-capacitacao",
    ),
    # GFP
    path(
        "gfp/ficha-financeira/",
        FichaFinanceiraRelatorioView.as_view(),
        name="gfp-relatorio-ficha-financeira",
    ),
    # Anotações Pessoais
    path(
        "anotacao-pessoal/anotacoes-pessoais/",
        AnotacaoPessoalRelatorioView.as_view(),
        name="anotacao_pessoal_relatorio_anotacoes_pessoais",
    ),
    path(
        "diarias/os-consolidada/",
        OsConsolidadaDiariasView.as_view(),
        name="diarias_os_consolidada",
    ),
    path(
        "diarias/prestacao-contas/",
        PrestacaoContasDiariasView.as_view(),
        name="diarias_prestacao_contas",
    ),
    # downloads
    path("download/", ReportDownloadFile.as_view(), name="download"),
    path("status/", ConsultaSituacaoRelatorio.as_view(), name="consulta_relatorio"),
    path("jasper/download/", PVFDownloadJasperFile.as_view(), name="download-jasper"),
]
