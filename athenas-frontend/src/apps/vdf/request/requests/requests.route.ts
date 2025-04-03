import { Route } from '@angular/router';
import { RequestsComponent } from './requests.component';

export const requestsRoute: Route[] = [
    {
        path: 'requests',
        component: RequestsComponent,
    },
    // {
    //     path: 'solicitacoes',
    //     component: RequestsComponent,
    // },
];
