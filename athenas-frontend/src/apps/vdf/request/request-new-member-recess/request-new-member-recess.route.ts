import { Route } from '@angular/router';
import { RequestNewMemberRecessComponent } from './request-new-member-recess.component';
import { RequestNewMemberRecessStep1Component } from './request-new-member-recess-step1/request-new-member-recess-step1.component';
import { RequestNewMemberRecessStep2Component } from './request-new-member-recess-step2/request-new-member-recess-step2.component';
import { RequestNewMemberRecessStep3Component } from './request-new-member-recess-step3/request-new-member-recess-step3.component';

export const RequestNewMemberRecessComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/recesso-forense-de-membros',
        component: RequestNewMemberRecessComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewMemberRecessStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewMemberRecessStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewMemberRecessStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/recesso-forense-de-membros/:step',
        component: RequestNewMemberRecessComponent,
    },
];
