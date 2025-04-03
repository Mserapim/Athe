import { Route } from '@angular/router';
import { RequestNewCompensatoryDaysComponent } from './request-new-compensatory-days.component';
import { RequestNewCompensatoryDaysStep1Component } from './request-new-compensatory-days-step1/request-new-compensatory-days-step1.component';
import { RequestNewCompensatoryDaysStep2Component } from './request-new-compensatory-days-step2/request-new-compensatory-days-step2.component';
import { RequestNewCompensatoryDaysStep3Component } from './request-new-compensatory-days-step3/request-new-compensatory-days-step3.component';

export const RequestNewCompensatoryDaysComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/folga-compensatoria',
        component: RequestNewCompensatoryDaysComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewCompensatoryDaysStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewCompensatoryDaysStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewCompensatoryDaysStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/folga-compensatoria/:step',
        component: RequestNewCompensatoryDaysComponent,
    },
];
