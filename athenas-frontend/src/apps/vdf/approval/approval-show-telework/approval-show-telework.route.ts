import { Route } from '@angular/router';
import { ApprovalShowTeleworkComponent } from './approval-show-telework.component';

export const ApprovalShowTeleworkRoute: Route[] = [
    {
        path: 'aprovacoes/visualizar/:requestId',
        component: ApprovalShowTeleworkComponent,
    },
];
