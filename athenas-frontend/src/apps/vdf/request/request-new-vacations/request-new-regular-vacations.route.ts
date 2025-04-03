import { Route } from '@angular/router';
import { RequestNewVacationsStep1Component } from './request-new-vacations-step1/request-new-vacations-step1.component';
import { RequestNewVacationsStep2Component } from './request-new-vacations-step2/request-new-vacations-step2.component';
import { RequestNewVacationsStep3Component } from './request-new-vacations-step3/request-new-vacations-step3.component';
import { RequestNewVacationsComponent } from './request-new-vacations.component';

export const REQUEST_NEW_VACATIONS_ROUTE_PATH =
    'solicitacoes/novo/ferias/:step';

export const requestNewRegularVacationsComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/ferias-regulamentares',
        component: RequestNewVacationsComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewVacationsStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewVacationsStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewVacationsStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/ferias-regulamentares/:step',
        component: RequestNewVacationsComponent,
    },
];
