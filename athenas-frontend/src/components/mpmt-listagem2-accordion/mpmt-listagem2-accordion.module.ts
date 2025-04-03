import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtListagem2AccordionComponent } from './mpmt-listagem2-accordion.component';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import {MatExpansionModule} from "@angular/material/expansion";
import {MatTableModule} from "@angular/material/table";
import {MpmtListagem2Module} from "../mpmt-listagem2/mpmt-listagem2.module";

const DECLARATIONS = [MpmtListagem2AccordionComponent];

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
        MatExpansionModule,
        MatTableModule,
        MpmtListagem2Module
    ],
})
export class MpmtListagem2AccordionModule {}
