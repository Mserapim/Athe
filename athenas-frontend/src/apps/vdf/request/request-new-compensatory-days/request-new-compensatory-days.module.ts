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
import { RequestNewCompensatoryDaysComponent } from './request-new-compensatory-days.component';
import { RequestNewCompensatoryDaysStep1Component } from './request-new-compensatory-days-step1/request-new-compensatory-days-step1.component';
import { RequestNewCompensatoryDaysStep2Component } from './request-new-compensatory-days-step2/request-new-compensatory-days-step2.component';
import { RequestNewCompensatoryDaysComponentRoute } from './request-new-compensatory-days.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestNewCompensatoryDaysService } from './request-new-compensatory-days.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewCompensatoryDaysStep3Component } from './request-new-compensatory-days-step3/request-new-compensatory-days-step3.component';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';

const route: Route[] = [...RequestNewCompensatoryDaysComponentRoute];

@NgModule({
    declarations: [
        RequestNewCompensatoryDaysComponent,
        RequestNewCompensatoryDaysStep1Component,
        RequestNewCompensatoryDaysStep2Component,
        RequestNewCompensatoryDaysStep3Component,
    ],
    providers: [RequestNewCompensatoryDaysService],
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
export class RequestNewCompensatoryDaysModule {}
