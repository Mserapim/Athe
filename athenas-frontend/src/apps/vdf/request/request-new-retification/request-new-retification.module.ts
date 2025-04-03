import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { RequestNewReticationComponent } from './request-new-retification.component';
import { requestNewRetificationComponentRoute } from './request-new-retification.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestNewRetificationStep1Component } from './request-new-retification-step1/request-new-retification-step1.component';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewRetificationStep2Component } from './request-new-retification-step2/request-new-retification-step2.component';
import { RequestNewRetificationService } from './request-new-retification.service';
import { RequestNewRetificationStep3Component } from './request-new-retification-step3/request-new-retification-step3.component';
import { RequestNewRetificationStep2DayoffComponent } from './request-new-retification-step2-dayoff/request-new-retification-step2-dayoff.component';

const route: Route[] = [...requestNewRetificationComponentRoute];

@NgModule({
    declarations: [
        RequestNewReticationComponent,
        RequestNewRetificationStep1Component,
        RequestNewRetificationStep2Component,
        RequestNewRetificationStep3Component,
        RequestNewRetificationStep2DayoffComponent,
    ],
    providers: [RequestNewReticationComponent, RequestNewRetificationService],
    imports: [
        MaterialModule,
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RequestStepperModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewReticationModule {}
