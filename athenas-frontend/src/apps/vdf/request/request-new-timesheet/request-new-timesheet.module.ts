import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { RequestNewTimesheetComponent } from './request-new-timesheet.component';
import { RequestNewTimesheetStepperComponent } from './request-new-timesheet-stepper/request-new-timesheet-stepper.component';
import { RequestNewTimesheetStep1Component } from './request-new-timesheet-step1/request-new-timesheet-step1.component';
import { RequestNewTimesheetStep2Component } from './request-new-timesheet-step2/request-new-timesheet-step2.component';
import { RequestNewTimesheetStepperService } from './request-new-timesheet-stepper/request-new-timesheet-stepper.service';
import { RequestNewTimesheetComponentRoute } from './request-new-timesheet.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestNewTimesheetStep2AddJustificationComponent } from './request-new-timesheet-step2-add-justification/request-new-timesheet-step2-add-justification.component';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestShowModule } from '../components/request-show/request-show.module';
import { RequestObservationAlertModule } from '../components/request-observation-alert/request-observation-alert.module';

const route: Route[] = [...RequestNewTimesheetComponentRoute];

@NgModule({
    declarations: [
        RequestNewTimesheetComponent,
        RequestNewTimesheetStepperComponent,
        RequestNewTimesheetStep1Component,
        RequestNewTimesheetStep2Component,
        RequestNewTimesheetStep2AddJustificationComponent,
    ],
    providers: [
        RequestNewTimesheetStepperService,
        RequestNewTimesheetStep1Component,
        RequestNewTimesheetStep2AddJustificationComponent,
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
        RequestObservationAlertModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewTimesheetModule {}
