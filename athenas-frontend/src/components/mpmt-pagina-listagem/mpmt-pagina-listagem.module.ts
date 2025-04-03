import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { MpmtPaginaListagemComponent } from './mpmt-pagina-listagem.component';
import { MpmtPaginaListagemBotoesComponent } from './mpmt-pagina-listagem-botoes/mpmt-pagina-listagem-botoes.component';
import { MpmtPaginaListagemTabelaComponent } from './mpmt-pagina-listagem-tabela/mpmt-pagina-listagem-tabela.component';
import { TableModule } from 'primeng/table';
import { MpmtPaginaListagemTabelaCelulaTextoComponent } from './mpmt-pagina-listagem-tabela-celula/mpmt-pagina-listagem-tabela-celula-texto/mpmt-pagina-listagem-tabela-celula-texto.component';
import { MpmtPaginaListagemTabelaCelulaNumericoComponent } from './mpmt-pagina-listagem-tabela-celula/mpmt-pagina-listagem-tabela-celula-numerico/mpmt-pagina-listagem-tabela-celula-numerico.component';
import { ButtonModule } from 'primeng/button';
import { MpmtPaginaListagemTabelaCelulaDataComponent } from './mpmt-pagina-listagem-tabela-celula/mpmt-pagina-listagem-tabela-celula-data/mpmt-pagina-listagem-tabela-celula-data.component';
import { PaginatorModule } from 'primeng/paginator';
import { MpmtPaginaListagemTabelaPaginacaoComponent } from './mpmt-pagina-listagem-tabela-paginacao/mpmt-pagina-listagem-tabela-paginacao.component';
import { MpmtPaginaListagemTabelaCelulaObjetoComponent } from './mpmt-pagina-listagem-tabela-celula/mpmt-pagina-listagem-tabela-celula-objeto/mpmt-pagina-listagem-tabela-celula-objeto.component';
import { MpmtPaginaListagemTabelaCelulaAcoesComponent } from './mpmt-pagina-listagem-tabela-celula/mpmt-pagina-listagem-tabela-celula-acoes/mpmt-pagina-listagem-tabela-celula-acoes.component';
import { MatMenuModule } from '@angular/material/menu';
import { ContextMenuModule } from 'primeng/contextmenu';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { MpmtPaginaListagemOpcoesComponent } from './mpmt-pagina-listagem-opcoes/mpmt-pagina-listagem-opcoes.component';
import { MpmtPaginaListagemFiltrosComponent } from './mpmt-pagina-listagem-filtros/mpmt-pagina-listagem-filtros.component';
import { MpmtPaginaListagemTabelaCelulaBoleanoIconeComponent } from './mpmt-pagina-listagem-tabela-celula/mpmt-pagina-listagem-tabela-celula-boleano-icone/mpmt-pagina-listagem-tabela-celula-boleano-icone.component';
import { MpmtPaginaListagemTabelaCelulaDataHoraComponent } from './mpmt-pagina-listagem-tabela-celula/mpmt-pagina-listagem-tabela-celula-data-hora/mpmt-pagina-listagem-tabela-celula-data-hora.component';

const DECLARATIONS = [
    MpmtPaginaListagemTabelaCelulaBoleanoIconeComponent,
    MpmtPaginaListagemComponent,
    MpmtPaginaListagemBotoesComponent,
    MpmtPaginaListagemTabelaComponent,
    MpmtPaginaListagemTabelaCelulaTextoComponent,
    MpmtPaginaListagemTabelaCelulaNumericoComponent,
    MpmtPaginaListagemFiltrosComponent,
    MpmtPaginaListagemOpcoesComponent,
    MpmtPaginaListagemTabelaCelulaDataComponent,
    MpmtPaginaListagemTabelaPaginacaoComponent,
    MpmtPaginaListagemTabelaCelulaObjetoComponent,
    MpmtPaginaListagemTabelaCelulaAcoesComponent,
    MpmtPaginaListagemTabelaCelulaDataHoraComponent,
]; 

@NgModule({
    declarations: DECLARATIONS, 
    exports: DECLARATIONS,   
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatMenuModule,
        LayoutModule,
        LayoutNavegacaoModule,
        FuseLoadingBarModule,
        MpmtPaginaTituloModule,
        ButtonModule,
        PopoverModule,
        TableModule,
        PaginatorModule, 
        ContextMenuModule,
        MenuModule,
    ],
})
export class MpmtPaginaListagemModule {}
