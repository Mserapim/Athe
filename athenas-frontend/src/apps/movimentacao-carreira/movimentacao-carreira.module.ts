import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Route, RouterModule } from '@angular/router';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtListagemModule } from 'components/mpmt-listagem/mpmt-listagem.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { MpmtPicklistModule } from 'components/mpmt-picklist/mpmt-picklist.module';
import { MatTreeModule } from '@angular/material/tree';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { movimentacaoCarreiraRoute } from './movimentacao-carreira.route';

import { MovimentacaoCarreiraListaAntiguidadesComponent } from './movimentacao-carreira-lista-antiguidades/movimentacao-carreira-lista-antiguidades.component';
import { MovimentacaoCarreiraListaAntiguidadesService } from './movimentacao-carreira-lista-antiguidades/movimentacao-carreira-lista-antiguidades.service';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { EstagioProbatorioMembrosComponent } from './estagio-probatorio-membros/estagio-probatorio-membros.component';
import { EstagioProbatorioMembrosService } from './estagio-probatorio-membros/estagio-probatorio-membros.service';
import { AfastamentoService } from './estagio-probatorio-membros/afastamentos-estagio-probatorio/afastamentos-estagio-probatorio.service';
import { AfastamentosComponent } from './estagio-probatorio-membros/afastamentos-estagio-probatorio/afastamentos-estagio-probatorio.component';
import { MpmtListagemSelecaoModule } from 'components/mpmt-listagens/mpmt-listagem-selecao/mpmt-listagem-selecao.module';
import { LayoutPadraoModalModule } from 'layout/mpmt-modal/layout-padrao-modal.module';

const ROUTES: Route[] = [...movimentacaoCarreiraRoute];

const DECLARATIONS = [
    MovimentacaoCarreiraListaAntiguidadesComponent, 
    EstagioProbatorioMembrosComponent, 
    AfastamentosComponent
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [
        MovimentacaoCarreiraListaAntiguidadesService, 
        EstagioProbatorioMembrosService, 
        AfastamentoService
    ],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MaterialModule,
        MpmtListagemModule,
        MpmtBotaoModule,
        MpmtSelecaoModule,
        MpmtPicklistModule,
        MatTreeModule,
        MatButtonModule,
        MpmtListagem2Module,
        MatIconModule,
        MpmtListagemSelecaoModule,
        LayoutPadraoModalModule,
        RouterModule.forChild(ROUTES),
    ],
    exports: [],
})
export class MovimentacaoCarreiraModule {}
