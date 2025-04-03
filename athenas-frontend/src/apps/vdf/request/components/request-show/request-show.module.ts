import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatInputModule } from '@angular/material/input';
import { RequestShowComponent } from './request-show.component';
import { RequestShowRoute } from './request-show.route';
import { RequestShowHistoricComponent } from './request-show-historic/request-show-historic.component';
import { RequestShowSubstitutesComponent } from './request-show-substitutes/request-show-substitutes.component';
import { RequestShowUsufructsComponent } from './request-show-usufructs/request-show-usufructs.component';
import { RequestShowDetailComponent } from './request-show-detail/request-show-detail.component';
import { RequestShowActionsComponent } from './request-show-actions/request-show-actions.component';
import { RequestShowTimesheetJustificationsComponent } from './request-show-timesheet-justifications/request-show-timesheet-justifications.component';
import { RequestShowTimesheetPendingsComponent } from './request-show-timesheet-pendings/request-show-timesheet-pendings.component';
import { RequestShowTeleworkTargetsComponent } from './request-show-telework-targets/request-show-telework-targets.component';
import { RequestShowRetificationsComponent } from './request-show-retifications/request-show-retifications.component';
import { RequestShowAbsencesComponent } from './request-show-absences/request-show-absences.component';
import { RequestShowServerShiftConfirmComponent } from './request-show-server-shift-confirm/request-show-server-shift-confirm.component';
import { RequestObservationModule } from '../request-observation/request-observation.module';
import { RequestShowExercicioCumulativoComponent } from './request-show-exercicio-cumulativo/request-show-exercicio-cumulativo.component';
import { RequestShowHorizontalProgressionsComponent } from './request-show-horizontal-progressions/request-show-horizontal-progressions.component';
import { RequestShowProgressaoVerticalComponent } from './request-show-progressao-vertical/request-show-progressao-vertical.component';
import { AtualizarExercicioCumulativoService } from './request-show-exercicio-cumulativo/request-show-exercicio-cumulativo.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestShowProgressaoVerticalCreateComponent } from './request-show-progressao-vertical/request-show-progressao-vertical-create/request-show-progressao-vertical-create.component';
import { RequestShowProgressaoVerticalRemoveComponent } from './request-show-progressao-vertical/request-show-progressao-vertical-remove/request-show-progressao-vertical-remove.component';
import { EditObservationModalComponent } from './request-show-observation-retification/request-show-observation-retification.component';
import { RequestShowCancelamentoTeletrabalhoComponent } from './request-show-cancelamento-teletrabalho/request-show-cancelamento-teletrabalho.component';
import { MpBotaoDownloadPdfModule } from 'components/mp-botao-download-pdf/mp-botao-download-pdf.module';
import { RequestShowRelatorioTeletrabalhoSemestralQuestionarioComponent } from './request-show-relatorio-teletrabalho-semestral-questionario/request-show-relatorio-teletrabalho-semestral-questionario.component';
import { RequestShowRelatorioTeletrabalhoSemestralServidoresComponent } from './request-show-relatorio-teletrabalho-semestral-servidores/request-show-relatorio-teletrabalho-semestral-servidores.component';
import { RequestShowTimesheetSolicitacaoAfastamentoComponent } from './request-show-timesheet-solicitacao-afastamento/request-show-timesheet-solicitacao-afastamento.component';
import { RequestShowSolicitacaoFolgaComponent } from './request-show-solicitacao-folga/request-show-solicitacao-folga.component';
import { RequestSolicitacaoFolgaEditarComponent } from './request-show-solicitacao-folga/request-solicitacao-folga-editar/request-solicitacao-folga-editar.component';
import { RequestShowSolicitacaoAuxilioCrecheIrComponent } from './request-show-solicitacao-auxilio-creche-ir/request-show-solicitacao-auxilio-creche-ir.component';
import { RequestSolicitacaoAuxilioCrecheIrEditarComponent } from './request-show-solicitacao-auxilio-creche-ir/request-solicitacao-auxilio-creche-ir-editar/request-solicitacao-auxilio-creche-ir-editar.component';
import { MpmtBotaoModule } from '../../../../../components/mpmt-botao/mpmt-botao.module';
import { RequestShowTeleworkAfastamentosComponent } from './request-show-telework-afastamentos/request-show-telework-afastamentos.component';
import { RequestShowCreditoDispensaEleitoralComponent } from './request-show-credito-dispensa-eleitoral/request-show-credito-dispensa-eleitoral.component';
import { MpmtFileUpdateModule } from '../../../../../components/mpmt-file-update/mpmt-file-update.module';
import { RequestShowTeletrabalhoDesbloqueioComponent } from './request-show-teletrabalho-desbloqueio/request-show-teletrabalho-desbloqueio.component';
import { RequestObservationAlertModule } from '../request-observation-alert/request-observation-alert.module';

const route: Route[] = [...RequestShowRoute];

const DECLARATIONS = [
    RequestShowComponent,
    RequestShowHistoricComponent,
    RequestShowSubstitutesComponent,
    RequestShowUsufructsComponent,
    RequestShowDetailComponent,
    RequestShowActionsComponent,
    RequestShowTimesheetJustificationsComponent,
    RequestShowTimesheetPendingsComponent,
    RequestShowTeleworkTargetsComponent,
    RequestShowRetificationsComponent,
    RequestShowAbsencesComponent,
    RequestShowServerShiftConfirmComponent,
    RequestShowExercicioCumulativoComponent,
    RequestShowHorizontalProgressionsComponent,
    RequestShowProgressaoVerticalComponent,
    RequestShowProgressaoVerticalCreateComponent,
    RequestShowProgressaoVerticalRemoveComponent,
    RequestShowCancelamentoTeletrabalhoComponent,
    RequestShowRelatorioTeletrabalhoSemestralServidoresComponent,
    RequestShowRelatorioTeletrabalhoSemestralQuestionarioComponent,
    RequestShowTimesheetSolicitacaoAfastamentoComponent,
    EditObservationModalComponent,
    RequestShowSolicitacaoFolgaComponent,
    RequestSolicitacaoFolgaEditarComponent,
    RequestShowSolicitacaoAuxilioCrecheIrComponent,
    RequestSolicitacaoAuxilioCrecheIrEditarComponent,
    RequestShowTeleworkAfastamentosComponent,
    RequestShowTeletrabalhoDesbloqueioComponent,
    RequestShowCreditoDispensaEleitoralComponent,
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [
        { provide: MAT_DIALOG_DATA, useValue: {} },
        RequestShowComponent,
        AtualizarExercicioCumulativoService,
        RequestShowComponent,
        RequestShowProgressaoVerticalCreateComponent,
        RequestShowProgressaoVerticalRemoveComponent,
    ],
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        ReactiveFormsModule,
        RequestObservationModule,
        MpBotaoDownloadPdfModule,
        MpmtBotaoModule,
        RequestObservationAlertModule,
        RouterModule.forChild(route),
        MpmtFileUpdateModule,
    ],
})
export class RequestShowModule {}
