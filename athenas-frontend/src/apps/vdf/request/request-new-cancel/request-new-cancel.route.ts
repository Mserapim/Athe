import { Route } from '@angular/router';
import { RequestNewCancelComponent } from './request-new-cancel.component';
import { RequestNewCancelStep1Component } from './request-new-cancel-step1/request-new-absence-step1.component';
import { RequestNewCancelStep2UsufrutosComponent } from './request-new-cancel-step2-usufrutos/request-new-cancel-step2-usufrutos.component';
import { RequestNewCancelStep2TeletrabalhoComponent } from './request-new-cancel-step2-teletrabalho/request-new-cancel-step2-teletrabalho.component';


export const requestNewCancelComponentRoute: Route[] = [
    {
        path: 'solicitacoes/cancelamento',
        component: RequestNewCancelComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewCancelStep1Component,
            },
            {
                path: 'step2/programacao',
                component: RequestNewCancelStep2UsufrutosComponent,
            },
            {
                path: 'step2/teletrabalho',
                component: RequestNewCancelStep2TeletrabalhoComponent,
            }
        ],
    },
    {
        path: 'solicitacoes/novo/plantao/:step',
        component: RequestNewCancelComponent,
    },
];
