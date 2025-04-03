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
import { RequestNewMemberRecessComponent } from './request-new-member-recess.component';
import { RequestNewMemberRecessStep1Component } from './request-new-member-recess-step1/request-new-member-recess-step1.component';
import { RequestNewMemberRecessStep2Component } from './request-new-member-recess-step2/request-new-member-recess-step2.component';
import { RequestNewMemberRecessComponentRoute } from './request-new-member-recess.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestNewMemberRecessService } from './request-new-member-recess.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewMemberRecessStep3Component } from './request-new-member-recess-step3/request-new-member-recess-step3.component';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';

const route: Route[] = [...RequestNewMemberRecessComponentRoute];

@NgModule({
    declarations: [
        RequestNewMemberRecessComponent,
        RequestNewMemberRecessStep1Component,
        RequestNewMemberRecessStep2Component,
        RequestNewMemberRecessStep3Component,
    ],
    providers: [RequestNewMemberRecessService],
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
export class RequestNewMemberRecessModule {}
