import { Route } from '@angular/router';
import { RequestNewAbsenceStep1Component } from './request-new-absence-step1/request-new-absence-step1.component';
import { RequestNewAbsenceComponent } from './request-new-absence.component';
import { RequestNewAbsenceStep2HealthLicenseComponent } from './request-new-absence-step2-health-license/request-new-absence-step2-health-licence.component';
import { RequestNewAbsenceStep3Component } from './request-new-absence-step3/request-new-absence-step3.component';
import { RequestNewAbsenceStep2HealthLicenseFamilyComponent } from './request-new-absence-step2-health-license-family/request-new-absence-step2-health-licence-family.component';
import { RequestNewAbsenceStep2PaternityAbsencesComponent } from './request-new-absence-step2-paternity-absences/request-new-absence-step2-paternity-absences.component';
import { RequestNewAbsenceStep2MourningComponent } from './request-new-absence-step2-mourning/request-new-absence-step2-mourning.component';
import { RequestNewAbsenceStep2MarriageComponent } from './request-new-absence-step2-marriage/request-new-absence-step2-marriage.component';
import { RequestNewAbsenceStep2MaternityAbsencesComponent } from './request-new-absence-step2-maternity/request-new-absence-step2-maternity.component';
import { RequestNewAbsenceStep2BloodDonationComponent } from './request-new-absence-step2-blood-donation/request-new-absence-step2-blood-donation.component';

export const REQUEST_NEW_ABSENCE_ROUTE_PATH =
    'solicitacoes/novo/ferias-regulamentares/:step';

export const requestNewAbsenceComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/afastamentos',
        component: RequestNewAbsenceComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewAbsenceStep1Component,
            },
            {
                path: 'step2/health-license',
                component: RequestNewAbsenceStep2HealthLicenseComponent,
            },
            {
                path: 'step2/health-license-family',
                component: RequestNewAbsenceStep2HealthLicenseFamilyComponent,
            },
            {
                path: 'step2/paternidade',
                component: RequestNewAbsenceStep2PaternityAbsencesComponent,
            },
            {
                path: 'step2/maternidade',
                component: RequestNewAbsenceStep2MaternityAbsencesComponent,
            },
            {
                path: 'step2/mourning',
                component: RequestNewAbsenceStep2MourningComponent,
            },
            {
                path: 'step2/marriage',
                component: RequestNewAbsenceStep2MarriageComponent,
            },
            // {
            //     path: 'step2/maternity',
            //     component: RequestNewAbsenceStep2PaternityAbsencesComponent,
            // },
            {
                path: 'step2/blood-donation',
                component: RequestNewAbsenceStep2BloodDonationComponent,
            },
            {
                path: 'step3',
                component: RequestNewAbsenceStep3Component,
            },
        ],
    },
    // {
    //     path: 'solicitacoes/novoafastamentos/:step',
    //     component: RequestNewAbsenceComponent,
    // },
];
