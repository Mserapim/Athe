import { Route } from '@angular/router';
import { RequestNewReticationComponent } from './request-new-retification.component';
import { RequestNewRetificationStep1Component } from './request-new-retification-step1/request-new-retification-step1.component';
import { RequestNewRetificationStep2Component } from './request-new-retification-step2/request-new-retification-step2.component';
import { RequestNewRetificationStep3Component } from './request-new-retification-step3/request-new-retification-step3.component';
import { RequestNewRetificationStep2DayoffComponent } from './request-new-retification-step2-dayoff/request-new-retification-step2-dayoff.component';

export const requestNewRetificationComponentRoute: Route[] = [
    {
        path: 'solicitacoes/retificacoes',
        component: RequestNewReticationComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewRetificationStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewRetificationStep2Component,
            },
            {
                path: 'step2/folgas',
                component: RequestNewRetificationStep2DayoffComponent,
            },
            {
                path: 'step3',
                component: RequestNewRetificationStep3Component,
            },
        ],
    },
];
