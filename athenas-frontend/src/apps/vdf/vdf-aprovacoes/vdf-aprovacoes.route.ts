import { Route } from '@angular/router';
import { VdfAprovacoesComponent } from './vdf-aprovacoes.component';

export const VdfAprovacoesRoute: Route[] = [
    {
        path: 'aprovacoes',
        component: VdfAprovacoesComponent,
    },
    {
        path: 'aprovacoes/pendentes',
        component: VdfAprovacoesComponent,
        data: {
            filtros: {
                pending_request: true,
            },
        },
    },
];
