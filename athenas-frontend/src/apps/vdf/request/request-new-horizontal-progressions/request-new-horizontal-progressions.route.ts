import { Route } from '@angular/router';
import { RequestNewHorizontalProgressionsComponent } from './request-new-horizontal-progressions.component';
import { RequestNewHorizontalProgressionsStep1Component } from './request-new-horizontal-progressions-step1/request-new-horizontal-progressions-step1.component';
import { RequestNewHorizontalProgressionsStep2Component } from './request-new-horizontal-progressions-step2/request-new-horizontal-progressions-step2.component';

export const RequestNewHorizontalProgressionsComponentRoute: Route[] = [
    {
        path: 'solicitacoes/progressao-horizontal',
        component: RequestNewHorizontalProgressionsComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewHorizontalProgressionsStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewHorizontalProgressionsStep2Component,
            },
        ],
    },
];
