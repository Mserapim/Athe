import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtAccordionComponent } from './mpmt-accordion.component';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import {MpmtCelulaModule} from "../mpmt-celula/mpmt-celula.module";

const DECLARATIONS = [MpmtAccordionComponent, ];

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
        MpmtPaginaTituloModule,
        ReactiveFormsModule,
        MpmtCelulaModule,
    ],
})
export class MpmtAccordionModule {}
