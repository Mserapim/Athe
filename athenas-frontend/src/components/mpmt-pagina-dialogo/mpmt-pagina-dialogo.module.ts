import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { MpmtPaginaDialogoComponent } from './mpmt-pagina-dialogo.component';
import { DialogService } from 'primeng/dynamicdialog';
import { MpmtPaginaDialogoService } from './mpmt-pagina-dialogo.service';

const DECLARATIONS = [
    MpmtPaginaDialogoComponent,
]; 

@NgModule({
    declarations: DECLARATIONS, 
    exports: [...DECLARATIONS],   
    providers: [DialogService, MpmtPaginaDialogoService],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule, 
        LayoutModule,
        LayoutNavegacaoModule,
        FuseLoadingBarModule,
        MpmtPaginaTituloModule, 
        ButtonModule,
        TableModule,
        DialogModule
    ],
})
export class MpmtPaginaDialogoModule {}
