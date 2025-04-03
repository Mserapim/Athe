import { Route } from '@angular/router';
import { GestaoPessoasGestaoVdfComponent } from './gestao-pessoas-gestao-vdf/gestao-pessoas-gestao-vdf.component';
import { GestorCargosComponent } from './gestor-cargos/gestor-cargos.component';

export const gestaoPessoasRoute: Route[] = [
    {
        path: 'gestao-vdf',
        component: GestaoPessoasGestaoVdfComponent,
    },
    {
        path: 'gestor-cargos',
        component: GestorCargosComponent,
    },
];
