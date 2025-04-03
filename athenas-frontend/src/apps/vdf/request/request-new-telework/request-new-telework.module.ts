import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { RequestNewTeleworkComponent } from './request-new-telework.component';
import { RequestNewTeleworkStep1Component } from './request-new-telework-step1/request-new-telework-step1.component';
import { RequestNewTeleworkStep2Component } from './request-new-telework-step2/request-new-telework-step2.component';
import { RequestNewTeleworkComponentRoute } from './request-new-telework.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewTeleworkService } from './request-new-telework.service';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';
import { RequestShowModule } from '../components/request-show/request-show.module';
import { MpBotaoDownloadPdfModule } from 'components/mp-botao-download-pdf/mp-botao-download-pdf.module';
import { MpPdfPreviewModule } from 'components/mp-pdf-preview/mp-pdf-preview.module';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { RequestNewTeleworkStep2DialogComponent } from './request-new-telework-step2-dialog/request-new-telework-step2-dialog.component';
import { LayoutPadraoModalModule } from 'layout/mpmt-modal/layout-padrao-modal.module';
import { MpmtTextoFormatadoModule } from 'components/mpmt-texto-formatado/mpmt-texto-formatado.module';
import { RequestObservationAlertModule } from '../components/request-observation-alert/request-observation-alert.module';

const route: Route[] = [...RequestNewTeleworkComponentRoute];

@NgModule({
    declarations: [
        RequestNewTeleworkComponent,
        RequestNewTeleworkStep1Component,
        RequestNewTeleworkStep2Component,
        RequestNewTeleworkStep2DialogComponent,
    ],
    providers: [RequestNewTeleworkService],
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
        RequestShowModule,
        MatDialogModule,
        MpmtTextoFormatadoModule,
        LayoutPadraoModalModule,
        RequestObservationAlertModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewTeleworkModule {}
