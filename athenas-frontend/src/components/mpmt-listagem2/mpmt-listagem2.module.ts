import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtListagem2Component } from './mpmt-listagem2.component';
import { MpmtListagem2CelulaComponent } from './mpmt-listagem2-celula/mpmt-listagem2-celula.component';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { CoreModule } from 'core/core.module';

const DECLARATIONS = [MpmtListagem2Component, MpmtListagem2CelulaComponent];

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
        ReactiveFormsModule,
        // CoreModule,
    ],
})
export class MpmtListagem2Module {}
