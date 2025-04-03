import { Route } from '@angular/router';
import { RequestShowUsufructComponent } from './request-show-usufruct.component';

export const RequestShowUsufructRoute: Route[] = [
    {
        path: 'solicitacoes/usufruto/:usufructId',
        component: RequestShowUsufructComponent,
    },
];
