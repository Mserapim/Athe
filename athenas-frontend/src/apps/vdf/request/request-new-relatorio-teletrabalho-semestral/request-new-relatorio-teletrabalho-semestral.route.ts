import { Route } from '@angular/router';
import { RequestNewRelatorioTeletrabalhoSemestralComponent } from './request-new-relatorio-teletrabalho-semestral.component';
import { RequestNewRelatorioTeletrabalhoSemestralStep1Component } from './request-new-relatorio-teletrabalho-semestral-step1/request-new-relatorio-teletrabalho-semestral-step1.component';
import { RequestNewRelatorioTeletrabalhoSemestralStep2Component } from './request-new-relatorio-teletrabalho-semestral-step2/request-new-relatorio-teletrabalho-semestral-step2.component';

export const RequestNewRelatorioTeletrabalhoSemestralComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/relatorio-teletrabalho-semestral',
        component: RequestNewRelatorioTeletrabalhoSemestralComponent,
        children: [
            {
                path: 'step1',
                component:
                    RequestNewRelatorioTeletrabalhoSemestralStep1Component,
            },
            {
                path: 'step2',
                component:
                    RequestNewRelatorioTeletrabalhoSemestralStep2Component,
            },
        ],
    },
];
