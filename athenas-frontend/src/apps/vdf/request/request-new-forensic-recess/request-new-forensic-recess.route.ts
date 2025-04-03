import { Route } from '@angular/router';
import { RequestNewForensicRecessComponent } from './request-new-forensic-recess.component';
import { RequestNewForensicRecessStep1Component } from './request-new-forensic-recess-step1/request-new-forensic-recess-step1.component';
import { RequestNewForensicRecessStep2Component } from './request-new-forensic-recess-step2/request-new-forensic-recess-step2.component';
import { RequestNewForensicRecessStep3Component } from './request-new-forensic-recess-step3/request-new-forensic-recess-step3.component';

export const RequestNewForensicRecessComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/recesso-forense',
        component: RequestNewForensicRecessComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewForensicRecessStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewForensicRecessStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewForensicRecessStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/recesso-forense/:step',
        component: RequestNewForensicRecessComponent,
    },
];
