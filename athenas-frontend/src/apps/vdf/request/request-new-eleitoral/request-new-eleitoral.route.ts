import { Route } from '@angular/router';
import { RequestNewEleitoralComponent } from './request-new-eleitoral.component';
import { RequestNewEleitoralStep2FolgaComponent } from './request-new-eleitoral-step2-folga/request-new-eleitoral-step2-folga.component';
import { RequestNewEleitoralStep3FolgaComponent } from './request-new-eleitoral-step3-folga/request-new-eleitoral-step3-folga.component';
import { RequestNewEleitoralStep4FolgaComponent } from './request-new-eleitoral-step4-folga/request-new-eleitoral-step4-folga.component';
import {RequestNewEleitoralStep1Component} from "./request-new-eleitoral-step1/request-new-eleitoral-step1.component";
import {
    RequestNewEleitoralStep2CreditoComponent
} from "./request-new-eleitoral-step2-credito/request-new-eleitoral-step2-credito.component";

export const requestNewEleitoralComponentRoute: Route[] = [

    {
        path: 'solicitacoes/novo/dispensa-eleitoral',
        component: RequestNewEleitoralComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewEleitoralStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewEleitoralStep2FolgaComponent,
            },
            {
                path: 'step3',
                component: RequestNewEleitoralStep3FolgaComponent,
            },
            {
                path: 'step4',
                component: RequestNewEleitoralStep4FolgaComponent,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/credito-eleitoral',
        component: RequestNewEleitoralComponent,
        children: [
            {
                path: 'step2',
                component: RequestNewEleitoralStep2CreditoComponent,
            },
            {
                path: 'step2/:idSoliitacao',
                component: RequestNewEleitoralStep2CreditoComponent,
            }
        ],
    },

    {
        path: 'solicitacoes/novo/dispensa-eleitoral/:step',
        component: RequestNewEleitoralComponent,
    },
    {
        path: 'solicitacoes/novo/credito-eleitoral/:step',
        component: RequestNewEleitoralComponent,
    },
    {
        path: 'solicitacoes/novo/credito-eleitoral/:step/:idSolicitacao',
        component: RequestNewEleitoralComponent,
    }
];
