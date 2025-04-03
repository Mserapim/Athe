import { Route } from '@angular/router';
import { RequestSolicitacaoFolgaComponent } from './request-new-solicitacao-folga.component';
import { RequestSolicitacaoFolgaStep1Component } from './request-new-solicitacao-folga-step1/request-new-solicitacao-folga-step1.component';

export const RequestNewSolicitacaoFolgaComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/solicitacao-folga',
        component: RequestSolicitacaoFolgaComponent,
        children: [
            {
                path: 'step1',
                component: RequestSolicitacaoFolgaStep1Component,
            },
        ],
    },
];
