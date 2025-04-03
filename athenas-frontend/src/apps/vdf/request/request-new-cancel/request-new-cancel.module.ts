import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { RequestNewCancelComponent } from './request-new-cancel.component';
import { requestNewCancelComponentRoute } from './request-new-cancel.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewCancelStep2UsufrutosComponent } from './request-new-cancel-step2-usufrutos/request-new-cancel-step2-usufrutos.component';
import { RequestNewCancelStep1Component } from './request-new-cancel-step1/request-new-absence-step1.component';
import { RequestNewCancelStep2TeletrabalhoComponent } from './request-new-cancel-step2-teletrabalho/request-new-cancel-step2-teletrabalho.component';

const route: Route[] = [...requestNewCancelComponentRoute];

@NgModule({
    declarations: [
        RequestNewCancelComponent,
        RequestNewCancelStep1Component,
        RequestNewCancelStep2TeletrabalhoComponent,
        RequestNewCancelStep2UsufrutosComponent,
    ],
    providers: [RequestNewCancelComponent],
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
export class RequestNewCancelModule {}
