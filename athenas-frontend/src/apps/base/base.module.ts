import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Route, RouterModule } from '@angular/router';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtListagemModule } from 'components/mpmt-listagem/mpmt-listagem.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { baseRoute } from './base.route';
import { BasePaginaNaoEncontradaComponent } from './base-pagina-nao-encontrada/base-pagina-nao-encontrada.component';

const ROUTES: Route[] = [...baseRoute];

const DECLARATIONS = [BasePaginaNaoEncontradaComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MaterialModule,
        MpmtListagemModule,
        MpmtBotaoModule,
        MpmtSelecaoModule,
        RouterModule.forChild(ROUTES),
    ],
    exports: [],
})
export class BaseModule {}
