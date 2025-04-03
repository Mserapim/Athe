import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { RequestNewSolicitacaoFolgaComponentRoute } from './request-new-solicitacao-folga.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewSolicitacaoFolgaService } from './request-new-solicitacao-folga.service';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';
import { RequestShowModule } from '../components/request-show/request-show.module';
import { MpBotaoDownloadPdfModule } from 'components/mp-botao-download-pdf/mp-botao-download-pdf.module';
import { MpPdfPreviewModule } from 'components/mp-pdf-preview/mp-pdf-preview.module';
import { RequestSolicitacaoFolgaStep1Component } from './request-new-solicitacao-folga-step1/request-new-solicitacao-folga-step1.component';
import { RequestSolicitacaoFolgaComponent } from './request-new-solicitacao-folga.component';

const route: Route[] = [...RequestNewSolicitacaoFolgaComponentRoute];

@NgModule({
    declarations: [
        RequestSolicitacaoFolgaComponent,
        RequestSolicitacaoFolgaStep1Component,
    ],
    providers: [RequestNewSolicitacaoFolgaService],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RequestStepperModule,
        RequestSubstitutesModule,
        RequestShowModule,
        MpBotaoDownloadPdfModule,
        MpPdfPreviewModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewSolicitacaoFolgaModule {}
