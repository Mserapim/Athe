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
import { RequestNewBloodDonationComponent } from './request-new-blood-donation.component';
import { RequestNewBloodDonationStep1Component } from './request-new-blood-donation-step1/request-new-blood-donation-step1.component';
import { RequestNewBloodDonationStep2Component } from './request-new-blood-donation-step2/request-new-blood-donation-step2.component';
import { RequestNewBloodDonationComponentRoute } from './request-new-blood-donation.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestNewBloodDonationService } from './request-new-blood-donation.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewBloodDonationStep3Component } from './request-new-blood-donation-step3/request-new-blood-donation-step3.component';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';

const route: Route[] = [...RequestNewBloodDonationComponentRoute];

@NgModule({
    declarations: [
        RequestNewBloodDonationComponent,
        RequestNewBloodDonationStep1Component,
        RequestNewBloodDonationStep2Component,
        RequestNewBloodDonationStep3Component,
    ],
    providers: [RequestNewBloodDonationService],
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
export class RequestNewBloodDonationModule {}
