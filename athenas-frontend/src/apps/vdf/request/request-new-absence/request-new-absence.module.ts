import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { RequestNewAbsenceComponent } from './request-new-absence.component';
import { RequestNewAbsenceStep1Component } from './request-new-absence-step1/request-new-absence-step1.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { requestNewAbsenceComponentRoute } from './request-new-absence.route';
import { MatFormFieldModule } from '@angular/material/form-field';
import { RequestNewAbsenceStepperComponent } from './request-new-absence-stepper-old/request-new-absence-stepper.component';
import { RequestNewAbsenceStep2HealthLicenseComponent } from './request-new-absence-step2-health-license/request-new-absence-step2-health-licence.component';
import { VdfRequestComponentsModule } from '../components/request-components.module';
import { RequestNewAbsenceStep3Component } from './request-new-absence-step3/request-new-absence-step3.component';
import { RequestNewAbsenceStep2HealthLicenseFamilyComponent } from './request-new-absence-step2-health-license-family/request-new-absence-step2-health-licence-family.component';
import { AutocompleteLibModule } from 'angular-ng-autocomplete';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { RequestNewAbsenceStep2PaternityAbsencesComponent } from './request-new-absence-step2-paternity-absences/request-new-absence-step2-paternity-absences.component';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { RequestNewAbsenceStep2MourningComponent } from './request-new-absence-step2-mourning/request-new-absence-step2-mourning.component';
import { RequestNewAbsenceStep2MarriageComponent } from './request-new-absence-step2-marriage/request-new-absence-step2-marriage.component';
import { RequestNewAbsenceStep2MaternityAbsencesComponent } from './request-new-absence-step2-maternity/request-new-absence-step2-maternity.component';
import { RequestNewAbsenceStep2BloodDonationComponent } from './request-new-absence-step2-blood-donation/request-new-absence-step2-blood-donation.component';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';
import { RequestNewAbsenceService } from './request-new-absence.service';
import { RequestPersonNewModule } from '../components/request-person-new/request-person-new.module';
const route: Route[] = [...requestNewAbsenceComponentRoute];

@NgModule({
    declarations: [
        RequestNewAbsenceComponent,
        RequestNewAbsenceStepperComponent,
        RequestNewAbsenceStep1Component,
        RequestNewAbsenceStep2HealthLicenseComponent,
        RequestNewAbsenceStep2HealthLicenseFamilyComponent,
        RequestNewAbsenceStep2PaternityAbsencesComponent,
        RequestNewAbsenceStep2MourningComponent,
        RequestNewAbsenceStep2MarriageComponent,
        RequestNewAbsenceStep2BloodDonationComponent,
        RequestNewAbsenceStep3Component,
        RequestNewAbsenceStep2MaternityAbsencesComponent,
    ],
    providers: [RequestNewAbsenceService],
    imports: [
        CommonModule,
        MatSnackBarModule,
        FormsModule,
        MatCheckboxModule,
        LayoutModule,
        MaterialModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        VdfRequestComponentsModule,
        AutocompleteLibModule,
        RequestStepperModule,
        RequestSubstitutesModule,
        RequestPersonNewModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewAbsenceModule {}
