import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatRadioModule } from '@angular/material/radio';
import { RequestNewServerShiftsComponent } from './request-new-server-shifts.component';
import { RequestNewServerShiftsStep1Component } from './request-new-server-shifts-step1/request-new-server-shifts-step1.component';
import { RequestNewServerShiftsStep2Component } from './request-new-server-shifts-step2/request-new-server-shifts-step2.component';
import { RequestNewServerShiftsComponentRoute } from './request-new-server-shifts.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestNewServerShiftsService } from './request-new-server-shifts.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewServerShiftsStep3Component } from './request-new-server-shifts-step3/request-new-server-shifts-step3.component';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';

const route: Route[] = [...RequestNewServerShiftsComponentRoute];

@NgModule({
    declarations: [
        RequestNewServerShiftsComponent,
        RequestNewServerShiftsStep1Component,
        RequestNewServerShiftsStep2Component,
        RequestNewServerShiftsStep3Component,
    ],
    providers: [RequestNewServerShiftsService],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatPaginatorModule,
        MatButtonModule,
        MatSelectModule,
        MatRadioModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        RequestStepperModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RequestSubstitutesModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewServerShiftsModule {}
