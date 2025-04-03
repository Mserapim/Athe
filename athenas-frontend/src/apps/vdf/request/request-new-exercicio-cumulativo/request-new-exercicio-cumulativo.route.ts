import { Route } from '@angular/router';
import { RequestNewExercicioCumulativoComponent } from './request-new-exercicio-cumulativo.component';
import { RequestNewExercicioCumulativoStep1Component } from './request-new-exercicio-cumulativo-step1/request-new-exercicio-cumulativo-step1.component';

export const RequestNewExercicioCumulativoComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/exercicio-cumulativo',
        component: RequestNewExercicioCumulativoComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewExercicioCumulativoStep1Component,
            },
        ],
    },
];
