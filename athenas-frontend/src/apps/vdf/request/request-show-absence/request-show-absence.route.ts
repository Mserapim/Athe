import { Route } from '@angular/router';
import { requestShowAbsenceComponent } from './request-show-absence.component';

export const requestShowAbsenceRoute: Route[] = [
    {
        path: 'solicitacoes/afastamentos/:usufructId',
        component: requestShowAbsenceComponent,
    },
];
