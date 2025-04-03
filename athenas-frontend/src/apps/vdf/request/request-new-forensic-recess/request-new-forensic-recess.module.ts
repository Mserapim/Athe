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
import { RequestNewForensicRecessComponent } from './request-new-forensic-recess.component';
import { RequestNewForensicRecessStep1Component } from './request-new-forensic-recess-step1/request-new-forensic-recess-step1.component';
import { RequestNewForensicRecessStep2Component } from './request-new-forensic-recess-step2/request-new-forensic-recess-step2.component';
import { RequestNewForensicRecessComponentRoute } from './request-new-forensic-recess.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestNewForensicRecessService } from './request-new-forensic-recess.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewForensicRecessStep3Component } from './request-new-forensic-recess-step3/request-new-forensic-recess-step3.component';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';

const route: Route[] = [...RequestNewForensicRecessComponentRoute];

@NgModule({
    declarations: [
        RequestNewForensicRecessComponent,
        RequestNewForensicRecessStep1Component,
        RequestNewForensicRecessStep2Component,
        RequestNewForensicRecessStep3Component,
    ],
    providers: [RequestNewForensicRecessService],
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
export class RequestNewForensicRecessModule {}
