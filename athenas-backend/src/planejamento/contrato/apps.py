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
class ContratoConfig(AppConfig):
    name = "planejamento.contrato"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        # CONTRATO
        "planejamento.contrato.views",
        "planejamento.contrato.reports",
        "planejamento.contrato.api.configuration",
        "planejamento.contrato.api.agreementaction",
        "planejamento.contrato.api.agreementannotation",
        "planejamento.contrato.api.additive",
        "planejamento.contrato.api.agreement",
        "planejamento.contrato.api.sendcnprovider",
        "planejamento.contrato.api.meterage",
        "planejamento.contrato.api.commitmentnote",
        "planejamento.contrato.api.outsourced",
        "planejamento.contrato.api.agreementvalue",
        "planejamento.contrato.api.supervisor",
        "planejamento.contrato.api.minute",
        "planejamento.contrato.api.minuteaction",
        "planejamento.contrato.api.minuteitem",
        "planejamento.contrato.api.minutesolicitation",
        "planejamento.contrato.api.report",
        "planejamento.contrato.api.hired",
        "planejamento.contrato.api.ride",
        "planejamento.contrato.api.enterprise",
        "planejamento.contrato.api.document",
        "planejamento.contrato.scripts",
    ]

    def ready(self):
        connect_signals()
        load_notify()
        register_statics()


def connect_signals():
    importlib.import_module("planejamento.contrato.signals")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:
        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/planejamento/hiring/configuration/MinuteConfiguration.js",
        "/%(context)s/static/planejamento/hiring/agreement/Grid.js",
        "/%(context)s/static/planejamento/hiring/agreement/Manage.js",
        "/%(context)s/static/planejamento/hiring/agreement/Restful.js",
        "/%(context)s/static/planejamento/hiring/agreement/Window.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportWindowBase.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportPaymentStatement.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportPaymentRoll.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportAgreeBalance.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportBankPayment.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportAgreeManager.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportAgreements.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportContractBalance.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportAgreeSupervisor.js",
        "/%(context)s/static/planejamento/hiring/agreement/ReportMonthReadjustment.js",
        "/%(context)s/static/planejamento/hiring/agreementvalue/Restful.js",
        "/%(context)s/static/planejamento/hiring/agreementvalue/Grid.js",
        "/%(context)s/static/planejamento/hiring/agreementvalue/Window.js",
        "/%(context)s/static/planejamento/hiring/commitmentnote/Restful.js",
        "/%(context)s/static/planejamento/hiring/commitmentnote/Grid.js",
        "/%(context)s/static/planejamento/hiring/commitmentnote/Window.js",
        "/%(context)s/static/planejamento/hiring/meterage/Restful.js",
        "/%(context)s/static/planejamento/hiring/meterage/Grid.js",
        "/%(context)s/static/planejamento/hiring/meterage/Window.js",
        "/%(context)s/static/planejamento/hiring/meterage/PaymentWindow.js",
        "/%(context)s/static/planejamento/hiring/meterage/ReportPayment.js",
        "/%(context)s/static/planejamento/hiring/meterage/DispatchTextWindow.js",
        "/%(context)s/static/planejamento/hiring/agreementaction/Restful.js",
        "/%(context)s/static/planejamento/hiring/agreementaction/Grid.js",
        "/%(context)s/static/planejamento/hiring/agreementaction/Window.js",
        "/%(context)s/static/planejamento/hiring/agreementannotation/Restful.js",
        "/%(context)s/static/planejamento/hiring/agreementannotation/Grid.js",
        "/%(context)s/static/planejamento/hiring/agreementannotation/Window.js",
        "/%(context)s/static/planejamento/hiring/agreementannotation/MinuteAnnotationRestful.js",
        "/%(context)s/static/planejamento/hiring/agreementannotation/MinuteAnnotationGrid.js",
        "/%(context)s/static/planejamento/hiring/agreementannotation/MinuteAnnotationWindow.js",
        "/%(context)s/static/planejamento/hiring/supervisor/SupervisorRestful.js",
        "/%(context)s/static/planejamento/hiring/supervisor/SupervisorGrid.js",
        "/%(context)s/static/planejamento/hiring/supervisor/SupervisorWindow.js",
        "/%(context)s/static/planejamento/hiring/supervisor/ClassificationRestful.js",
        "/%(context)s/static/planejamento/hiring/supervisor/ClassificationGrid.js",
        "/%(context)s/static/planejamento/hiring/supervisor/ClassificationWindow.js",
        "/%(context)s/static/planejamento/hiring/supervisor/AgreementSupervisorRestful.js",
        "/%(context)s/static/planejamento/hiring/supervisor/AgreementSupervisorGrid.js",
        "/%(context)s/static/planejamento/hiring/supervisor/AgreementSupervisorWindow.js",
        "/%(context)s/static/planejamento/hiring/supervisor/MinuteSupervisorRestful.js",
        "/%(context)s/static/planejamento/hiring/supervisor/MinuteSupervisorGrid.js",
        "/%(context)s/static/planejamento/hiring/supervisor/MinuteSupervisorWindow.js",
        "/%(context)s/static/planejamento/hiring/supervisor/CloseSupervisorWindow.js",
        "/%(context)s/static/planejamento/hiring/minute/MinuteRestful.js",
        "/%(context)s/static/planejamento/hiring/minute/MinuteGrid.js",
        "/%(context)s/static/planejamento/hiring/minute/MinuteWindow.js",
        "/%(context)s/static/planejamento/hiring/minute/MinuteManage.js",
        "/%(context)s/static/planejamento/hiring/minuteaction/MinuteActionGrid.js",
        "/%(context)s/static/planejamento/hiring/minuteaction/MinuteActionWindow.js",
        "/%(context)s/static/planejamento/hiring/minuteaction/MinuteActionRestful.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemRestful.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemValidatorRestful.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemGrid.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemGridValidator.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemWindow.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemWindowValidator.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemGroupWindow.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemComplementaryDescriptionRestful.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemComplementaryDescriptionGrid.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemComplementaryDescriptionWindow.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemActionGrid.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemActionWindow.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemActionRestful.js",
        "/%(context)s/static/planejamento/hiring/minuteitem/MinuteItemUploadFileWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationGrid.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationItemRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationItemGrid.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationItemWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationItemDescriptionRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitation/MinuteSolicitationItemDescriptionGrid.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationaction/MinuteSolicitationActionRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationaction/MinuteSolicitationActionGrid.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationaction/MinuteSolicitationActionWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationcommitmentnote/MinuteSolicitationCommitmentNoteRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationcommitmentnote/MinuteSolicitationCommitmentNoteGrid.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationcommitmentnote/MinuteSolicitationCommitmentNoteWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationpayment/MinuteSolicitationPaymentRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationpayment/MinuteSolicitationPaymentGrid.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationpayment/MinuteSolicitationPaymentWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationpayment/MinuteSolicitationPaymentExecutionWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationManagerRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationManagerGrid.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationManagerGridAdmin.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationManagerManage.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationManagerManageAdmin.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationManagerWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationAgreementParameterWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/EdocTextWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationRebalancingWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/MinuteSolicitationRebalancingRestful.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationmanager/SolicitationRebalancingWindow.js",
        "/%(context)s/static/planejamento/hiring/minutesolicitationrequisition/MinuteSolicitationRequisitionRestful.js",
        "/%(context)s/static/planejamento/hiring/minutereport/BaseReportWindow.js",
        "/%(context)s/static/planejamento/hiring/minutereport/MinuteListReport.js",
        "/%(context)s/static/planejamento/hiring/minutereport/MinuteListBySupervisorReport.js",
        "/%(context)s/static/planejamento/hiring/minutereport/MinuteExportXLS.js",
        "/%(context)s/static/planejamento/hiring/minutereport/ContractAdditivesTerm.js",
        "/%(context)s/static/planejamento/hiring/minutereport/ContratoExportXLS.js",
        "/%(context)s/static/planejamento/hiring/minutereport/FiscalReportList.js",
        "/%(context)s/static/planejamento/hiring/minutereport/SolicitationListReport.js",
        "/%(context)s/static/planejamento/hiring/minutereport/SolicitationListByMinuteReport.js",
        "/%(context)s/static/planejamento/hiring/minutereport/SolicitationListPaymentByMinuteReport.js",
        "/%(context)s/static/planejamento/hiring/minutereport/SolicitationListByObjectMinuteReport.js",
        "/%(context)s/static/planejamento/hiring/minutereport/ReportMinuteSupervisor.js",
        "/%(context)s/static/planejamento/hiring/hired/Restful.js",
        "/%(context)s/static/planejamento/hiring/hired/Grid.js",
        "/%(context)s/static/planejamento/hiring/hired/Window.js",
        "/%(context)s/static/planejamento/hiring/ride/Restful.js",
        "/%(context)s/static/planejamento/hiring/ride/Grid.js",
        "/%(context)s/static/planejamento/hiring/ride/Window.js",
        "/%(context)s/static/planejamento/hiring/ride/Manage.js",
        "/%(context)s/static/planejamento/hiring/ride/ReportListMinuteAdhesion.js",
        "/%(context)s/static/planejamento/hiring/ride/ReportAccession.js",
        "/%(context)s/static/planejamento/hiring/ride/ReportMembershipBalanceMinute.js",
        "/%(context)s/static/planejamento/hiring/rideitem/Restful.js",
        "/%(context)s/static/planejamento/hiring/rideitem/Grid.js",
        "/%(context)s/static/planejamento/hiring/rideitem/GridBottom.js",
        "/%(context)s/static/planejamento/hiring/rideitem/Window.js",
        "/%(context)s/static/planejamento/hiring/enterprise/Restful.js",
        "/%(context)s/static/planejamento/hiring/enterprise/Grid.js",
        "/%(context)s/static/planejamento/hiring/enterprise/Window.js",
        "/%(context)s/static/planejamento/hiring/enterprise/Manage.js",
        "/%(context)s/static/planejamento/hiring/corporatestructure/Restful.js",
        "/%(context)s/static/planejamento/hiring/corporatestructure/Grid.js",
        "/%(context)s/static/planejamento/hiring/corporatestructure/Window.js",
        "/%(context)s/static/planejamento/hiring/document/DocumentManager.js",
        "/%(context)s/static/planejamento/hiring/document/DocumentRestful.js",
        "/%(context)s/static/planejamento/hiring/document/DocumentWindow.js",
        "/%(context)s/static/planejamento/hiring/document/DocumentGrid.js",
        "/%(context)s/static/planejamento/hiring/document/AgreementDocumentRestful.js",
        "/%(context)s/static/planejamento/hiring/document/AgreementDocumentWindow.js",
        "/%(context)s/static/planejamento/hiring/document/AgreementDocumentGrid.js",
        "/%(context)s/static/planejamento/hiring/document/ValueDocumentRestful.js",
        "/%(context)s/static/planejamento/hiring/document/ValueDocumentWindow.js",
        "/%(context)s/static/planejamento/hiring/document/ValueDocumentGrid.js",
        "/%(context)s/static/planejamento/hiring/document/MinuteDocumentRestful.js",
        "/%(context)s/static/planejamento/hiring/document/MinuteDocumentWindow.js",
        "/%(context)s/static/planejamento/hiring/document/MinuteDocumentGrid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="planejamento")

    """Registro dos Stylesheet para este aplicativo"""
    Application.register_stylesheet(
        "/%(context)s/static/planejamento/hiring/images/agree.css"
    )


def load_notify():
    importlib.import_module("planejamento.contrato.notify")
