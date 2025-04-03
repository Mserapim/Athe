import { Route } from '@angular/router';
import { RequestNewServerShiftsComponent } from './request-new-server-shifts.component';
import { RequestNewServerShiftsStep1Component } from './request-new-server-shifts-step1/request-new-server-shifts-step1.component';
import { RequestNewServerShiftsStep2Component } from './request-new-server-shifts-step2/request-new-server-shifts-step2.component';
import { RequestNewServerShiftsStep3Component } from './request-new-server-shifts-step3/request-new-server-shifts-step3.component';

export const RequestNewServerShiftsComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/plantao-servidor',
        component: RequestNewServerShiftsComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewServerShiftsStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewServerShiftsStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewServerShiftsStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/plantao-servidor/:step',
        component: RequestNewServerShiftsComponent,
    },
];
