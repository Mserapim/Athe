import { Route } from '@angular/router';
import { PainelControleModulosComponent } from './painel-controle-modulos/painel-controle-modulos.component';
import { PainelControleNavegacaoComponent } from './painel-controle-navegacao/painel-controle-navegacao.component';
import {
    PainelControleGruposComponent
} from "./painel-controle-grupos/painel-controle-grupos.component";
import { PainelControleUsuariosComponent } from './painel-controle-usuarios/painel-controle-usuarios.component';
import { PainelControleServicosComponent } from './painel-controle-servicos/painel-controle-servicos.component';
import { PainelControleConfigPontoComponent } from './painel-controle-configuracao-configuracao-de-ponto/painel-controle-configuracao-configuracao-de-ponto.component'
import { PainelControleHistoricoServicosComponent } from './painel-controle-historico-servicos/painel-controle-historico-servicos.component';
import { AuditoriaLogsComponent } from './painel-controle-auditoria-logs/painel-controle-auditoria-logs.component';

export const painelControleRoute: Route[] = [
    {
        path: 'modulos',
        component: PainelControleModulosComponent,
    },
    {
        path: 'navegacao',
        component: PainelControleNavegacaoComponent,
    },
    {
        path: 'grupo-acesso',
        component: PainelControleGruposComponent,
    },
    {
        path: 'usuarios',
        component: PainelControleUsuariosComponent,
    },
    {
        path: 'servicos',
        component: PainelControleServicosComponent,
    },
    {
        path: 'configuracao-de-ponto',
        component: PainelControleConfigPontoComponent,
    },
    {
        path: 'historico-servicos',
        component: PainelControleHistoricoServicosComponent,
    },
    {
        path: 'auditoria-logs',
        component: AuditoriaLogsComponent,
    },
];
