import { Route } from '@angular/router';
import { RequestShowTeleworkComponent } from './request-show-telework.component';

export const RequestShowTeleworkRoute: Route[] = [
    {
        path: 'solicitacoes/teletrabalho/:teleworkId',
        component: RequestShowTeleworkComponent,
    },
];
