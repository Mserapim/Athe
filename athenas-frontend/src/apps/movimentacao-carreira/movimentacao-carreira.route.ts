import { Route } from '@angular/router';
import { MovimentacaoCarreiraListaAntiguidadesComponent } from './movimentacao-carreira-lista-antiguidades/movimentacao-carreira-lista-antiguidades.component';
import { EstagioProbatorioMembrosComponent } from './estagio-probatorio-membros/estagio-probatorio-membros.component';

export const movimentacaoCarreiraRoute: Route[] = [
    {
        path: 'cadastros/lista-antiguidades',
        component: MovimentacaoCarreiraListaAntiguidadesComponent,
    },
    {
        path: 'estagio-probatorio/membros',
        component: EstagioProbatorioMembrosComponent,
    },
];
