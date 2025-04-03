import { Route } from '@angular/router';
import { BasePaginaNaoEncontradaComponent } from './base-pagina-nao-encontrada/base-pagina-nao-encontrada.component';

export const baseRoute: Route[] = [
    {
        path: 'pagina-nao-encontrada',
        component: BasePaginaNaoEncontradaComponent,
    },
];
