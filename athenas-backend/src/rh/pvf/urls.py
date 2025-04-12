from django.urls import path, include
from rest_framework import routers
from rh.pvf.apiv2.views.auxiliocrechedependenteirview import (
    PVFSolicitacaoCreteAuxCrecheDepenIRView,
    PVFSolicitacaoReenvioAuxCrecheDepenIRDetalhes,
    PVFSolicitacaoReenvioAuxCrecheDepenIRView,
)
from rh.pvf.apiv2.views.baseviews import *
from rh.pvf.apiv2.views.calendarviews import *
from rh.pvf.apiv2.views.exerciciocumulativoview import *
from rh.pvf.apiv2.views.historyretificationviews import *
from rh.pvf.apiv2.views.progressionviews import *
from rh.pvf.apiv2.views.serverdutyviews import *
from rh.pvf.apiv2.views.solicitacaofolgaview import *
from rh.pvf.apiv2.views.usufructviews import *
from rh.pvf.apiv2.views.myrightviews import *
from rh.pvf.apiv2.views.absenceviews import *
from rh.pvf.apiv2.views.approvalviews import *
from rh.pvf.apiv2.views.cancelviews import *
from rh.pvf.apiv2.views.retificationviews import *
from rh.pvf.apiv2.views.sendteleworkviews import *
from rh.pvf.apiv2.views.sendtimesheetviews import *
from rh.pvf.apiv2.views.configviews import *
from rh.pvf.apiv2.views.solicitacaodispensaeleitoralview import *


router = routers.DefaultRouter()


# config views
router.register(
    "config/server-shifts/permissions/types",
    PVFConfigTypeShiftViewSet,
    basename="config_server-shifts_permissions_types",
)
router.register(
    "config/server-shifts/types",
    PVFTypeShiftViewSet,
    basename="config_server-shifts_types",
)
router.register(
    "config/requests/types", PVFConfigTypeViewSet, basename="config_requests_types"
)
router.register(
    "config/requests/status", PVFConfigStatusViewSet, basename="config_requests_status"
)
router.register(
    "config/requests/approvers",
    PVFConfigStepViewSet,
    basename="config_requests_approvers",
)
router.register(
    "config/requests/teleworks/target-situations",
    PVFConfigMarkSituationViewSet,
    basename="config_requests_teleworks_target-situations",
)
router.register(
    "config/requests/designations",
    PVFDesignationViewSet,
    basename="config_requests_designations",
)
router.register(
    "config/requests/candidate-substitutes",
    PVFSubstituteCandidateViewSet,
    basename="config_requests_candidate-substitutes",
)
router.register(
    "config/requests/employees",
    PVFApprovalsEmployeeViewSet,
    basename="config_requests_employees",
)
router.register(
    "config/requests/acquisition-periods",
    PVFAcquisitionPeriodViewSet,
    basename="config_requests_acquisition-periods",
)
router.register(
    "config/requests/absences/types",
    PVFTypeAbsenceViewSet,
    basename="config_requests_absences_types",
)
router.register(
    "config/requests/persons", PVFPersonViewSet, basename="config_requests_persons"
)
router.register(
    "config/requests/cancel/usufructs",
    PVFCancelUsufrctViewSet,
    basename="config_requests_cancel_usufructs",
)
router.register(
    "config/requests/retifications/usufructs",
    PVFRetificationUsufructViewSet,
    basename="config_requests_retifications_usufructs",
)
router.register(
    "config/reports/types-payroll",
    PVFTypesPayrollViewSet,
    basename="config_reports_types-payroll",
)
router.register(
    "config/user/types-request",
    PVFTipoSolicitacaoView,
    basename="config_user_types-request",
)
router.register("config/workplaces", PVFWorkplaceViewSet, basename="config_workplaces")
router.register("config/employees", PVFEmployeeViewSet, basename="config_employees")
router.register("config/cids", PVFConfigCIDView, basename="config_cids")
router.register(
    "config/tipos-cancelamento",
    PVFConfigTipoCancelamentoView,
    basename="config_tipos-cancelamento",
)


# myright views
router.register("myrights", PVFMyRightsViewSet, basename="myrights")
router.register(
    "myrights/acquisition-periods",
    PVFMyRightsAqPeriodViewSet,
    basename="myrights_acquisition-periods",
)

# usufruct views
router.register(
    "requests/usufructs/regular-vacations",
    PVFRegularVacationViewSet,
    basename="requests_usufructs_regular-vacations",
)
router.register(
    "requests/usufructs/individual-vacations",
    PVFIndividualVacationViewSet,
    basename="requests_usufructs_individual-vacations",
)
router.register(
    "requests/usufructs/electoral-slack",
    PVFElectoralSlackViewSet,
    basename="requests_usufructs_electoral-slack",
)
router.register(
    "requests/usufructs/forensic-recess",
    PVFForensicRecessViewSet,
    basename="requests_usufructs_forensic-recess",
)
router.register(
    "requests/usufructs/server-shifts",
    PVFServerShiftViewSet,
    basename="requests_usufructs_server-shifts",
)
router.register(
    "requests/usufructs/trainees-contest",
    PVFIntershipCompetitionViewSet,
    basename="requests_usufructs_trainees-contest",
)
router.register(
    "requests/usufructs/compensatory-days",
    PVFCompClearanceMembersViewSet,
    basename="requests_usufructs_compensatory-days",
)
router.register(
    "requests/usufructs/member-recess",
    PVFCompVactionMembersViewSet,
    basename="requests_usufructs_member-recess",
)
router.register(
    "requests/usufructs/substitute-promoters",
    PVFSubstitutePromoterContestViewSet,
    basename="requests_usufructs_substitute-promoters",
)
router.register(
    "requests/usufructs/blood-donation",
    PVFBloodDonationViewSet,
    basename="requests_usufructs_blood-donation",
)
router.register(
    "requests/usufructs/intern-recess",
    PVFSolicitacaoEstagiarioView,
    basename="requests_usufructs_intern-recess",
)
router.register(
    "requests/usufructs/resident-recess",
    PVFSolicitacaoResidenteView,
    basename="requests_usufructs_resident-recess",
)


router.register(
    "requests/schedules/cancel",
    PVFCancelScheduleViewSet,
    basename="requests_schedules_cancel",
)
router.register(
    "requests/schedules/retifications",
    PVFRetificationScheduleViewSet,
    basename="requests_schedules_retifications",
)

# absences views
router.register(
    "requests/absences/health-licenses",
    PVFHealthTreatmentAbsenceViewSet,
    basename="requests_absences_health-licenses",
)
router.register(
    "requests/absences/health-family-licenses",
    PVFHealtFamiliyDeseaseViewSet,
    basename="requests_absences_health-family-licenses",
)
router.register(
    "requests/absences/maternity-absences",
    PVFMaternityAbsenceViewSet,
    basename="requests_absences_maternity-absences",
)
router.register(
    "requests/absences/paternity-absences",
    PVFBirthAbsenceViewSet,
    basename="requests_absences_paternity-absences",
)
router.register(
    "requests/absences/mourning-absences",
    PVFDeathAbsenceViewSet,
    basename="requests_absences_mourning-absences",
)
router.register(
    "requests/absences/marriage-absences",
    PVFMarriageAbsenceViewSet,
    basename="requests_absences_marriage-absences",
)
router.register(
    "requests/absences/blood-donation",
    PVFBloodDonationAbsenceViewSet,
    basename="requests_absences_blood-donation",
)

# sendtelework views
router.register(
    "requests/sending/teleworks",
    PVFCreateTeleworkViewSet,
    basename="requests_sending_teleworks",
)
router.register(
    "requests/sending/teleworks/targets",
    PVFMarkTeleworkViewSet,
    basename="requests_sending_teleworks_targets",
)

# sendtimesheet views
router.register(
    "requests/sending/timesheets",
    PVFCreateSendingTimeSheetViewSet,
    basename="requests_sending_timesheets",
)
router.register(
    "requests/sending/timesheets/justifications",
    PVFPointJustificationViewSet,
    basename="requests_sending_timesheets_justifications",
)

# progressions
router.register(
    "requests/movements/horizontal-progressions",
    PVFCreateRequestProgressionHViewSet,
    basename="requests_movements_horizontal-progressions",
)
router.register(
    "requests/movements/horizontal-progressions/documents",
    PVFDocumentProgressionHViewSet,
    basename="requests_movements_horizontal-progressions_documents",
)
router.register(
    "requests/movements/vertical-progressions/documents",
    PVFDocumentProgressionVViewSet,
    basename="requests_movements_vertical-progressions_documents",
)
router.register(
    "horizontal-progressions/current",
    PVFMovProgressionHViewSet,
    basename="horizontal-progressions_current",
)
router.register(
    "horizontal-progressions/next",
    PVFConfigProgressionHViewSet,
    basename="horizontal-progressions_next",
)

# Exercicio cumulativo
router.register(
    "requests/venda/exercicios-cumulativos",
    PVFExercicioCumulativoView,
    basename="requests_venda_exercicios-cumulativos",
)

# Cancelamento Teletrabalho
router.register(
    "requests/teletrabalho/cancelar",
    PVFCancelamentoTeletrabalhoView,
    basename="requests_teletrabalho_cancelar",
)

# Relatório Semestral
router.register(
    "requests/envios/relatorio-semestral/teletrabalhos",
    PVFRelatorioSemestralTeletrabalhoView,
    basename="requests_envios_relatorio-semestral_teletrabalhos",
)

# calendarviews
router.register("event-groups", PVFConfigGroupEventView, basename="event-groups")

urlpatterns = [
    path("requests/", PVFRequestView.as_view(), name="requests"),
    path("requests/<int:pk>/", PVFRequestViewDetail.as_view(), name="request-detail"),
    path(
        "scales/server-shifts/",
        PVFCriarListarPlantoesServidores.as_view(),
        name="plantoes-servidores-criar-listar",
    ),
    path(
        "scales/server-shifts/<int:pk>/",
        PVFServeDutyViewSet.as_view(),
        name="plantoes-servidores-atualizar-detalhes",
    ),
    # calendarviews
    path("events/", PVFCalendarView.as_view(), name="events"),
    path("employee-teams/", PVFEmployeeTeamView.as_view(), name="employee_team"),
    path("event-types/", PVFEventTypeView.as_view(), name="event_types"),
    path("mypendecies/", PVFMyPendeciesView.as_view(), name="my_pendecies"),
    path(
        "minhas-substituicoes/",
        PVFMinhasSubstituicoesView.as_view(),
        name="minhas_substituicoes",
    ),
    path(
        "venda-substituicoes/",
        PVFVendaSubstituicoesView.as_view(),
        name="venda_substituicoes",
    ),
    path(
        "myrights/acquisition-periods/<int:pk>/attachments/",
        PVFAttachmentAqPeriodViewSet.as_view({"get": "attachments"}),
        name="attachments",
    ),
    path(
        "myrights/acquisition-periods/<int:pk>/usufructs/",
        PVFMyRightsUsufructViewSet.as_view({"get": "usufructs"}),
        name="usufructs",
    ),
    path(
        "requests/usufructs/pre-validate/",
        PVFPreValidacaoUsufrutoView.as_view(),
        name="pre_validate",
    ),
    path(
        "requests/absences/pre-validate/",
        PVFPreValidacaoAfastamentoView.as_view(),
        name="pre_validate",
    ),
    path(
        "requests/<int:pk>/histories/",
        PVFHistoryViewSet.as_view({"get": "request_histories"}),
        name="request_histories",
    ),
    path(
        "requests/<int:pk>/observation-retification/",
        PVFObservationRetificationViewSet.as_view({"post": "retificate_observation"}),
        name="observation-retification",
    ),
    path(
        "requests/<int:pk>/usufructs/",
        PVFUsufrctViewSet.as_view({"get": "request_usufructs"}),
        name="request_usufructs",
    ),
    path(
        "requests/<int:pk>/usufruct-retifications/",
        PVFUsufrutoRetificadoView.as_view({"get": "usufrutos_retificados"}),
        name="usufrutos_retificados",
    ),
    path(
        "requests/<int:pk>/payment/",
        PVFAlterarPagamentoUsufrutoViewSet.as_view({"post": "payment"}),
        name="payment",
    ),
    path(
        "requests/<int:pk>/substitutes/",
        PVFSubstituteViewSet.as_view({"get": "request_substitutes"}),
        name="request_substitutes",
    ),
    path(
        "requests/<int:pk>/cancel/",
        PVFRequestCancelViewSet.as_view({"post": "cancel"}),
        name="cancel",
    ),
    path(
        "requests/<int:pk>/teleworks/targets/",
        PVFListMarkTeleworkView.as_view({"get": "request_targets"}),
        name="request_targets",
    ),
    path(
        "requests/<int:pk>/sending-teleworks/",
        PVFSendTeleworkViewSet.as_view({"post": "send"}),
        name="send_teleworks",
    ),
    path(
        "requests/<int:pk>/timesheets/justifications/",
        PVFListPointJustificationView.as_view({"get": "request_justifications"}),
        name="request_justifications",
    ),
    path(
        "requests/<int:pk>/sending-timesheets/",
        PVFSendingTimeSheetViewSet.as_view({"post": "send"}),
        name="send_timesheets",
    ),
    path(
        "requests/<int:pk>/timesheets/pendencies/",
        PVFPendingTimeSheetView.as_view({"get": "request_pendencies"}),
        name="request_pendencies",
    ),
    path(
        "requests/<int:pk>/horizontal-progressions/documents/",
        PVFListDocumentProgressionView.as_view(
            {"get": "request_document_progressions"}
        ),
        name="horizontal_progressions",
    ),
    path(
        "requests/<int:pk>/vertical-progressions/documents/",
        PVFListDocumentProgressionVerticalView.as_view(
            {"get": "request_document_progressions"}
        ),
        name="vertical_progressions",
    ),
    path(
        "requests/<int:pk>/sending-progressions/",
        PVFSendProgressionHViewSet.as_view({"post": "send"}),
        name="send_horizontal_progressions",
    ),
    path(
        "requests/<int:pk>/server-shifts/",
        PVFRequestServeDutyViewSet.as_view({"get": "request_server_shifts"}),
        name="request_server_shifts",
    ),
    path(
        "requests/<int:pk>/enviar/exercicios-cumulativos/",
        PVFEnviarExercicioCumulativoView.as_view({"post": "send"}),
        name="enviar_exercicio_cumulativo",
    ),
    path(
        "requests/<int:pk>/exercicios-cumulativos/substituicoes/",
        PVFListaSubstiuicaoView.as_view({"get": "lista_substituicoes"}),
        name="lista_substuições",
    ),
    path(
        "venda-substituicoes/<int:pk>/indeferir/",
        PVFIndeferirExercicioCumulativoView.as_view({"post": "indeferir"}),
        name="indeferir",
    ),
    path(
        "requests/<int:pk>/exercicios-cumulativos/dias-consolidados/",
        PVFDiasConsolidadoView.as_view({"get": "dias_consolidados"}),
    ),
    path(
        "requests/<int:pk>/cancelamentos/teletrabalhos/",
        PVFListaCancelamentoTeletrabalhoView.as_view(
            {"get": "solicitacoes_teletrabalho"}
        ),
        name="lista_teletrabalhos",
    ),
    path(
        "requests/envios/teletrabalhos/",
        PVFListaTeletrabalhoView.as_view(),
        name="lista_teletrabalhos",
    ),
    path(
        "requests/lista/relatorio-semestral/teletrabalhos/",
        PVFListaRelatorioSemestralTeletrabalhoView.as_view(),
        name="lista-relatorio-semestral-teletrabalho",
    ),
    path(
        "approvals/requests/",
        PVFWaitingApprovalViewSet.as_view(),
        name="approvals-requests",
    ),
    path(
        "approvals/requests/<int:pk>/",
        PVFRequestViewDetail.as_view(),
        name="approvals-requests-detail",
    ),
    path(
        "approvals/requests/<int:pk>/authorize/",
        PVFRequestAuthorizeViewSet.as_view({"post": "authorize"}),
        name="authorize",
    ),
    path(
        "approvals/requests/<int:pk>/actions/",
        PVFApprovalActionsView.as_view({"get": "actions"}),
        name="config_actions",
    ),
    path(
        "config/requests/vacation-configs/",
        PVFVactionConfigView.as_view(),
        name="vacation_config",
    ),
    path(
        "config/requests/timesheets/references/",
        PVFReferenceTimeSheetView.as_view(),
        name="reference_timesheet",
    ),
    path(
        "config/requests/timesheets/justification-itens/",
        PVFJustificationItensView.as_view(),
        name="justifications_itens",
    ),
    path(
        "config/employees/teleworks/status/",
        PVFConfigTeleworkEmployeeView.as_view(),
        name="telework_config",
    ),
    path(
        "config/employees/timesheet/status/",
        PVFEnvioPedenteFolhaPontoView.as_view(),
        name="folha_ponto_pendente",
    ),
    path(
        "config/reports/timesheets/years/",
        PVFListYearPointSheetView.as_view(),
        name="point_sheets_years",
    ),
    path(
        "config/reports/paychecks/years/",
        PVFListYearPayCheckView.as_view(),
        name="paychecks_years",
    ),
    path("config/reports/months", PVFListMonthView.as_view(), name="months"),
    path(
        "config/reports/calendar/teams/",
        PVFListCalendarTeamsView.as_view(),
        name="calendar_teams",
    ),
    path(
        "config/reports/calendar/years/",
        PVFListYearCalendarView.as_view(),
        name="calendar_years",
    ),
    path(
        "config/reports/calendar/types/",
        PVFListTypeCalendarView.as_view(),
        name="calendar_types",
    ),
    path(
        "config/reports/financial-statement/years/",
        PVFListaAnoFichaFinanceiraView.as_view(),
        name="lista_anos_ficha_financeira",
    ),
    path(
        "config/requests/employee-types/",
        PVFConfigTypeEmployeeView.as_view(),
        name="lista",
    ),
    path(
        "config/requests/venda/periodo-substituicoes/",
        PVFSubstituicaoConfigPeridoVendaView.as_view(),
        name="config_venda_substituicao",
    ),
    path("", include(router.urls)),
]


urlpatternsvdf = [
    path(
        "solicitacao-folhaponto-afastamentos/",
        PVFFolhaPontoAfastamentoView.as_view(),
        name="solicitacoes-afastamentos",
    ),
    path("config-tipos-folgas/", PVFConfigTipoFolga.as_view(), name="tipo-folgas"),
    path(
        "config/requests/acoes/", PVFHistoricoConfigAcaoView.as_view(), name="tipo-acao"
    ),
    path(
        "config/requests/servidores/",
        PVFServidoresView.as_view(),
        name="lista-servidores",
    ),
    path(
        "solicitacao-folga/",
        PVFDetalhesSolicitacaoFolga.as_view(),
        name="detalhes-solicitacao-folga",
    ),
    path(
        "solicitacao-folga/criar/",
        PVFSolicitacaoFolga.as_view(),
        name="solicitacao-folga-criar",
    ),
    path(
        "solicitacao-folga/editar/",
        PVFSolicitacaoFolga.as_view(),
        name="solicitacao-folga-editar",
    ),
    path(
        "solicitacao-dispensa-eleitoral/",
        PVFDetalhesSolicitacaoDispensaEleitoral.as_view(),
        name="detalhes-solicitacao-dispensa-eleitoral",
    ),
    path(
        "solicitacao-dispensa-eleitoral/criar/",
        PVFSolicitacaoDispensaEleitoral.as_view(),
        name="solicitacao-dispensa-eleitoral-criar",
    ),
    path(
        "solicitacao-dispensa-eleitoral/editar/",
        PVFSolicitacaoDispensaEleitoral.as_view(),
        name="solicitacao-dispensa-eleitoral-editar",
    ),
    path(
        "solicitacao-aux-creche-ir/",
        PVFSolicitacaoReenvioAuxCrecheDepenIRDetalhes.as_view(),
        name="solicitacao-detalhes-aux-creche-depen-ir",
    ),
    path(
        "solicitacao-aux-creche-ir/criar/",
        PVFSolicitacaoCreteAuxCrecheDepenIRView.as_view(),
        name="solicitacao-criar-aux-creche-depen-ir",
    ),
    path(
        "solicitacao-aux-creche-ir/reenviar/",
        PVFSolicitacaoReenvioAuxCrecheDepenIRView.as_view({"post": "reenviar"}),
        name="solicitacao-reenviar-aux-creche-depen-ir",
    ),
    path(
        "solicitacao-desbloqueio-teletrabalho/criar/",
        PVFDesbloqueioTeletrabalhoView.as_view(),
        name="solicitacao-desbloqueio-teletrabalho",
    ),
    path(
        "infos-teletrabalho-bloqueado/",
        PVFInfoTeleBloqueado.as_view(),
        name="info-teletrabalho-bloqueado",
    ),
    path(
        "solicitacao-historico-anexos/",
        PVFHistoricoAnexoView.as_view(),
        name="solicitacao-historico-anexos",
    ),
    path(
        "requests/sending/teleworks/afastamentos/",
        PVFSolicitacaoTeletrabalhoAfastamentos.as_view(),
        name="solicitacao-teletrabalho-afastamentos",
    ),
]
