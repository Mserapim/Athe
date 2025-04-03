import { Route } from '@angular/router';
import { RequestNewBloodDonationComponent } from './request-new-blood-donation.component';
import { RequestNewBloodDonationStep1Component } from './request-new-blood-donation-step1/request-new-blood-donation-step1.component';
import { RequestNewBloodDonationStep2Component } from './request-new-blood-donation-step2/request-new-blood-donation-step2.component';
import { RequestNewBloodDonationStep3Component } from './request-new-blood-donation-step3/request-new-blood-donation-step3.component';

export const RequestNewBloodDonationComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/doacao-sangue',
        component: RequestNewBloodDonationComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewBloodDonationStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewBloodDonationStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewBloodDonationStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/doacao-sangue/:step',
        component: RequestNewBloodDonationComponent,
    },
];
