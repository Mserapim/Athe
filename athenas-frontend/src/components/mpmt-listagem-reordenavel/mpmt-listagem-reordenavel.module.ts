import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { MpmtListagemReordenavelComponent } from './mpmt-listagem-reordenavel.component';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';

const DECLARATIONS = [MpmtListagemReordenavelComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: DECLARATIONS,
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        DragDropModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        MpmtBotaoModule,
        FormsModule,
        MpmtPaginaTituloModule,
        ReactiveFormsModule,
    ],
})
export class MpmtListagemReordenavelModule {}
