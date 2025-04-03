import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { RequestNewRelatorioTeletrabalhoSemestralComponent } from './request-new-relatorio-teletrabalho-semestral.component';
import { RequestNewRelatorioTeletrabalhoSemestralStepperComponent } from './request-new-relatorio-teletrabalho-semestral-stepper/request-new-relatorio-teletrabalho-semestral-stepper.component';
import { RequestNewRelatorioTeletrabalhoSemestralStep1Component } from './request-new-relatorio-teletrabalho-semestral-step1/request-new-relatorio-teletrabalho-semestral-step1.component';
import { RequestNewRelatorioTeletrabalhoSemestralStep2Component } from './request-new-relatorio-teletrabalho-semestral-step2/request-new-relatorio-teletrabalho-semestral-step2.component';
import { RequestNewRelatorioTeletrabalhoSemestralStepperService } from './request-new-relatorio-teletrabalho-semestral-stepper/request-new-relatorio-teletrabalho-semestral-stepper.service';
import { RequestNewRelatorioTeletrabalhoSemestralComponentRoute } from './request-new-relatorio-teletrabalho-semestral.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestShowModule } from '../components/request-show/request-show.module';

const route: Route[] = [
    ...RequestNewRelatorioTeletrabalhoSemestralComponentRoute,
];

@NgModule({
    declarations: [
        RequestNewRelatorioTeletrabalhoSemestralComponent,
        RequestNewRelatorioTeletrabalhoSemestralStepperComponent,
        RequestNewRelatorioTeletrabalhoSemestralStep1Component,
        RequestNewRelatorioTeletrabalhoSemestralStep2Component,
    ],
    providers: [
        RequestNewRelatorioTeletrabalhoSemestralStepperService,
        RequestNewRelatorioTeletrabalhoSemestralStep1Component,
    ],
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
        RequestShowModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewRelatorioTeletrabalhoSemestralModule {}
