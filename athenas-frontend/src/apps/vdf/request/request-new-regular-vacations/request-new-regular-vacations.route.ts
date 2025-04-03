import { Route } from '@angular/router';
import { RequestNewRegularVacationsStep1Component } from './request-new-regular-vacations-step1/request-new-regular-vacations-step1.component';
import { RequestNewRegularVacationsStep2Component } from './request-new-regular-vacations-step2/request-new-regular-vacations-step2.component';
import { RequestNewRegularVacationsStep3Component } from './request-new-regular-vacations-step3/request-new-regular-vacations-step3.component';
import { RequestNewRegularVacationsComponent } from './request-new-regular-vacations.component';

export const REQUEST_NEW_REGULAR_VACATIONS_ROUTE_PATH =
    'solicitacoes/novo/ferias-regulamentares/:step';

export const requestNewRegularVacationsComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/ferias-regulamentares',
        component: RequestNewRegularVacationsComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewRegularVacationsStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewRegularVacationsStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewRegularVacationsStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/ferias-regulamentares/:step',
        component: RequestNewRegularVacationsComponent,
    },
];
