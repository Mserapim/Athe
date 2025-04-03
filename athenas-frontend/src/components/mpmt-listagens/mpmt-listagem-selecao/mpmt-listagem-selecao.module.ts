import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { MpmtListagemSelecaoComponent } from './mpmt-listagem-selecao.component';
import { MpmtCelulaModule } from 'components/mpmt-celula/mpmt-celula.module';

const DECLARATIONS = [MpmtListagemSelecaoComponent];

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
        ReactiveFormsModule,
        MpmtCelulaModule
    ],
})
export class MpmtListagemSelecaoModule {}
