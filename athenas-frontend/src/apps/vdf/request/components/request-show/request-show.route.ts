import { Route } from '@angular/router';
import { RequestShowComponent } from './request-show.component';

export const RequestShowRoute: Route[] = [
    {
        path: 'solicitacoes/usufruto/:usufructId',
        component: RequestShowComponent,
    },
];
