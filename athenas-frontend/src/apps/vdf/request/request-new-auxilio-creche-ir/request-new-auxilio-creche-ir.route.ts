import { Route } from '@angular/router';
import { RequestNewAuxilioCrecheIrComponent } from './request-new-auxilio-creche-ir.component';
import { RequestNewAuxilioCrecheIrStep1Component } from './request-new-auxilio-creche-ir-step1/request-new-auxilio-creche-ir-step1.component';

export const RequestNewExercicioCumulativoComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/auxilio-creche-ir',
        component: RequestNewAuxilioCrecheIrComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewAuxilioCrecheIrStep1Component,
            },
        ],
    },
];
