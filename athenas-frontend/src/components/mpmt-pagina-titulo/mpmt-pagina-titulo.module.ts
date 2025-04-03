import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtPaginaTituloComponent } from './mpmt-pagina-titulo.component';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';

const DECLARATIONS = [MpmtPaginaTituloComponent];

@NgModule({
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        LayoutModule,
        LayoutNavegacaoModule,
        FuseLoadingBarModule,
    ],
})
export class MpmtPaginaTituloModule {}
