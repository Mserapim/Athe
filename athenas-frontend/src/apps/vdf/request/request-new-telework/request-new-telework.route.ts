import { Route } from '@angular/router';
import { RequestNewTeleworkComponent } from './request-new-telework.component';
import { RequestNewTeleworkStep1Component } from './request-new-telework-step1/request-new-telework-step1.component';
import { RequestNewTeleworkStep2Component } from './request-new-telework-step2/request-new-telework-step2.component';

export const RequestNewTeleworkComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/teletrabalho',
        component: RequestNewTeleworkComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewTeleworkStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewTeleworkStep2Component,
            },
        ],
    },
];
