import { Route } from '@angular/router';
import { ESocialItensTabelaComponent } from "./itens-tabela/e-social-itens-tabela.component";
import {
    ESocialQualificacaoCadastralComponent
} from "./qualificacao-cadastral/e-social-qualificacao-cadastral.component";
import {ESocialConfiguracoesComponent} from "./configuracoes/e-social-configuracoes.component";

export const ESocialRoute: Route[] = [
    {
        path: 'tabela/itens-tabela',
        component: ESocialItensTabelaComponent,
    },
    {
        path: 'qualificacao-cadastral',
        component: ESocialQualificacaoCadastralComponent,
    },
    {
        path: 'configuracoes',
        component: ESocialConfiguracoesComponent,
    }
];
