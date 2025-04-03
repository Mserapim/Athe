import { Route } from '@angular/router';
import { AnotacoesPessoaisListagemComponent } from './anotacoes-pessoais-listagem/anotacoes-pessoais-listagem.component';
import { AnotacoesPessoaisPublicacoesComponent } from './anotacoes-pessoais-publicacoes/anotacoes-pessoais-publicacoes.component';

export const anotacoesPessoaisRoute: Route[] = [
    {
        path: 'anotacoes-pessoais',
        component: AnotacoesPessoaisListagemComponent,
    },
    {
        path: 'publicacoes',
        component: AnotacoesPessoaisPublicacoesComponent,
    },
];
