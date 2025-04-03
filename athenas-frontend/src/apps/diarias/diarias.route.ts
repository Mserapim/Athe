import { Route } from '@angular/router';
import { DiariasConfigCargosComponent } from './config/config-cargos/config-cargos.component';
import { DiariasConfigFluxosComponent } from './config/diarias-config-fluxos/diarias-config-fluxos.component';
import { DiariasConfigValoresComponent } from './config/config-valores/config-valores.component';
import { DiariasGruposAprovadoresComponent } from './config/grupo-aprovador/grupos-aprovadores/grupos-aprovadores.component';
import { ViagensComponent } from './gestao/viagem/viagens.component';
import { VerDiariaComponent } from './gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.component';
import { LimitesDiariasComponent } from './config/limite-diarias/limites-diarias.component';
import { PrestacoesContasComponent } from './gestao/prestacao-contas/prestacoes-contas.component';
import { DiariasGestaoPagamentosComponent } from './gestao/pagamentos/diaria-pagamentos.component';
import { DiariasConfigImportacaoComponent } from './config/importacao/importacao.component';

export const diariasRoute: Route[] = [
    {
        path: 'config/cargos',
        component: DiariasConfigCargosComponent,
    },
    {
        path: 'config/fluxos',
        component: DiariasConfigFluxosComponent,
    },
    {
        path: 'config/valores',
        component: DiariasConfigValoresComponent,
    },
    {
        path: 'config/grupos-aprovadores',
        component: DiariasGruposAprovadoresComponent,
    },
    {
        path: 'gestao/viagens',
        component: ViagensComponent,
    },
    {
        path: 'gestao/viagens/viagem',
        component: VerDiariaComponent,
    },
    {
        path: 'config/limites-diarias',
        component: LimitesDiariasComponent,
    },
    {
        path: 'gestao/prestacao-contas',
        component: PrestacoesContasComponent,
    },
    {
        path: 'gestao/pagamentos',
        component: DiariasGestaoPagamentosComponent,
    },
    {
        path: 'config/importacao',
        component: DiariasConfigImportacaoComponent,
    },
];
