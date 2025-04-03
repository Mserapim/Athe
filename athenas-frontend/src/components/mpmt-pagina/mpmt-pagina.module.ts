import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MpmtPaginaComponent } from './mpmt-pagina.component';

const DECLARATIONS = [MpmtPaginaComponent];

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        LayoutModule,
        LayoutNavegacaoModule,
        FuseLoadingBarModule,
    ],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
})
export class MpmtPaginaModule {}
