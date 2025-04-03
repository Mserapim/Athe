import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FullCalendarModule } from '@fullcalendar/angular';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { VdfHomeModule } from './home/home.module';
import { VdfCalendarModule } from './calendar/calendar.module';
import { VdfApprovalsModule } from './approval/approvals/approvals.module';
import { RequestNewRegularVacationsModule } from './request/request-new-regular-vacations/request-new-regular-vacations.module';
import { VdfRequestsModule } from './request/requests/requests.module';
import { RequestNewAbsenceModule } from './request/request-new-absence/request-new-absence.module';
import { RequestNewElectoralSlackModule } from './request/request-new-electoral-slack/request-new-electoral-slack.module';
import { RequestShowUsufructModule } from './request/request-show-usufruct/request-show-usufruct.module';
import { RequestShowAbsenceModule } from './request/request-show-absence/request-show-absence.module';
import { ApprovalShowUsufructModule } from './approval/approval-show-usufruct/approval-show-usufruct.module';
import { VdfMyRightsModule } from './my-rights/my-rights.module';
import { VdfClockingModule } from './clocking/clocking.module';
import { VdfReportsModule } from './reports/reports.module';
import { MaterialModule } from 'shared/material/material.module';
import { RequestNewCancelModule } from './request/request-new-cancel/request-new-cancel.module';
import { RequestNewHorizontalProgressionsModule } from './request/request-new-horizontal-progressions/request-new-horizontal-progressions.module';
import { VdfServerShiftModule } from './server-shift/server-shift.module';
import { RequestShowTeleworkModule } from './request/request-show-telework/request-show-telework.module';
import { RequestNewTeleworkModule } from './request/request-new-telework/request-new-telework.module';
import { RequestNewTimesheetModule } from './request/request-new-timesheet/request-new-timesheet.module';
import { RequestNewMenuModule } from './request/request-new-menu/request-new-menu.module';
import { ApprovalShowTeleworkModule } from './approval/approval-show-telework/approval-show-telework.module';
import { RequestNewReticationModule } from './request/request-new-retification/request-new-retification.module';
import { RequestNewVacationsModule } from './request/request-new-vacations/request-new-vacations.module';
import { RequestNewServerShiftsModule } from './request/request-new-server-shifts/request-new-server-shifts.module';
import { RequestNewForensicRecessModule } from './request/request-new-forensic-recess/request-new-forensic-recess.module';
import { RequestNewBloodDonationModule } from './request/request-new-blood-donation/request-new-blood-donation.module';
import { RequestNewTraineesContextModule } from './request/request-new-trainees-contest/request-new-trainees-contest.module';
import { RequestNewCompensatoryDaysModule } from './request/request-new-compensatory-days/request-new-compensatory-days.module';
import { RequestNewMemberRecessModule } from './request/request-new-member-recess/request-new-member-recess.module';
import { RequestNewSubstitutePromotersModule } from './request/request-new-substitute-promoters/request-new-substitute-promoters.module';
import { VdfMinhasSubstituicoesModule } from './minhas-substituicoes/minhas-substituicoes.module';
import { VdfRequestModule } from './request/request.module';
import { VdfMinhasAnotacoesModule } from './minhas-anotacoes/minhas-anotacoes.module';
import { RequestNewRelatorioTeletrabalhoSemestralModule } from './request/request-new-relatorio-teletrabalho-semestral/request-new-relatorio-teletrabalho-semestral.module';
import { RequestNewSolicitacaoFolgaModule } from './request/request-new-solicitacao-folga/request-new-solicitacao-folga.module';
import { VdfMinhasDiariasModule } from './minhas-diarias/minhas-diarias.module';
import { VdfAprovacoesModule } from './vdf-aprovacoes/vdf-aprovacoes.module';
import { VdfPlantoesModule } from './vdf-plantoes/vdf-plantoes.module';
import { VdfSolicitacoesModule } from './vdf-solicitacoes/vdf-solicitacoes.module';
import { VdfFolhaPontoModule } from './vdf-folha-ponto/vdf-folha-ponto.module';
import {RequestNewEleitoralModule} from "./request/request-new-eleitoral/request-new-eleitoral.module";
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarModule } from './vdf-solicitacao-teletrabalho-desbloqueio-criar/vdf-solicitacao-teletrabalho-desbloqueio-criar.module';
import { VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirModule } from './vdf-solicitacao-teletrabalho-desbloqueio-indeferir/vdf-solicitacao-teletrabalho-desbloqueio-indeferir.module';

@NgModule({
    declarations: [],
    providers: [
        // {
        //     provide: MAT_DATE_LOCALE, //TODO mover para global
        //     useValue: 'pt-BR',
        // },
    ],
    imports: [
        CommonModule,
        LayoutModule,
        FormsModule,
        MaterialModule,
        ReactiveFormsModule,
        FullCalendarModule,
        RequestNewTeleworkModule,
        RequestShowTeleworkModule,
        RequestNewRegularVacationsModule,
        RequestNewElectoralSlackModule,
        RequestNewEleitoralModule,
        RequestNewForensicRecessModule,
        RequestNewServerShiftsModule,
        RequestNewBloodDonationModule,
        RequestShowUsufructModule,
        RequestShowAbsenceModule,
        RequestNewAbsenceModule,
        RequestNewTimesheetModule,
        ApprovalShowUsufructModule,
        ApprovalShowTeleworkModule,
        RequestNewMenuModule,
        RequestNewHorizontalProgressionsModule,
        VdfHomeModule,
        VdfCalendarModule,
        VdfRequestsModule,
        VdfApprovalsModule,
        VdfMyRightsModule,
        VdfReportsModule,
        VdfClockingModule,
        VdfMinhasSubstituicoesModule,
        VdfMinhasAnotacoesModule,
        VdfServerShiftModule,
        RequestNewCancelModule,
        RequestNewReticationModule,
        RequestNewVacationsModule,
        RequestNewTraineesContextModule,
        RequestNewCompensatoryDaysModule,
        RequestNewMemberRecessModule,
        RequestNewSubstitutePromotersModule,
        RequestNewRelatorioTeletrabalhoSemestralModule,
        RequestNewSolicitacaoFolgaModule,
        VdfRequestModule,
        VdfMinhasDiariasModule,
        VdfAprovacoesModule,
        VdfPlantoesModule,
        VdfSolicitacoesModule,
        VdfFolhaPontoModule,
        VdfSolicitacaoTeletrabalhoDesbloqueioCriarModule,
        VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirModule,
    ],
})
export class VdfModule {}
