import { Route } from '@angular/router';
import { RequestNewSubstitutePromotersComponent } from './request-new-substitute-promoters.component';
import { RequestNewSubstitutePromotersStep1Component } from './request-new-substitute-promoters-step1/request-new-substitute-promoters-step1.component';
import { RequestNewSubstitutePromotersStep2Component } from './request-new-substitute-promoters-step2/request-new-substitute-promoters-step2.component';
import { RequestNewSubstitutePromotersStep3Component } from './request-new-substitute-promoters-step3/request-new-substitute-promoters-step3.component';

export const RequestNewSubstitutePromotersComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/concurso-promotor-substituto',
        component: RequestNewSubstitutePromotersComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewSubstitutePromotersStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewSubstitutePromotersStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewSubstitutePromotersStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/concurso-promotor-substituto/:step',
        component: RequestNewSubstitutePromotersComponent,
    },
];
