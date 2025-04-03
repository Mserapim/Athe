import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { MpmtCabecalhoListagemComponent } from './mpmt-cabecalho-listagem.component';

const DECLARATIONS = [MpmtCabecalhoListagemComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: DECLARATIONS,
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        MpmtBotaoModule,
        MpmtPaginaTituloModule,
        ReactiveFormsModule
    ],
})
export class MpmtCabecalhoListagemModule {}