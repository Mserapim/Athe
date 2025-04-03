import { Route } from '@angular/router';
import { ApprovalShowUsufructComponent } from './approval-show-usufruct.component';

export const ApprovalShowUsufructRoute: Route[] = [
    {
        path: 'aprovacoes/visualizar/:requestId',
        component: ApprovalShowUsufructComponent,
    },
];
