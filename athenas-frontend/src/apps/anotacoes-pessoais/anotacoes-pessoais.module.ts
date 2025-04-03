import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Route, RouterModule } from '@angular/router';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtListagemModule } from 'components/mpmt-listagem/mpmt-listagem.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { MpmtPicklistModule } from 'components/mpmt-picklist/mpmt-picklist.module';
import { MatTreeModule } from '@angular/material/tree';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { MpmtSelecaoIconesModule } from '../../components/mpmt-selecao-icones/mpmt-selecao-icones.module';
import { MpmtPaginaTituloModule } from 'components/mpmt-pagina-titulo/mpmt-pagina-titulo.module';
import { FuseDrawerModule } from '@fuse/components/drawer';
import { MpmtPicklistPaginadoApiModule } from '../../components/mpmt-picklist-paginado-api/mpmt-picklist-paginado-api.module';
import { anotacoesPessoaisRoute } from './anotacoes-pessoais.route';
import { AnotacoesPessoaisListagemService } from './anotacoes-pessoais-listagem/anotacoes-pessoais-listagem.service';
import { AnotacoesPessoaisListagemComponent } from './anotacoes-pessoais-listagem/anotacoes-pessoais-listagem.component';
import { AnotacoesPessoaisNovoComponent } from './anotacoes-pessoais-novo/anotacoes-pessoais-novo.component';
import { CKEditorModule } from '@ckeditor/ckeditor5-angular';
import { AnotacoesPessoaisPublicacoesComponent } from './anotacoes-pessoais-publicacoes/anotacoes-pessoais-publicacoes.component';
import { AnotacoesPessoaisPublicacoesService } from './anotacoes-pessoais-publicacoes/anotacoes-pessoais-publicacoes.service';
import { AnotacoesPessoaisEditarComponent } from './anotacoes-pessoais-editar/anotacoes-pessoais-editar.component';
import { AnotacoesPessoaisVisualizarComponent } from './anotacoes-pessoais-visualizar/anotacoes-pessoais-visualizar.component';
import { MpmtTextoFormatadoModule } from 'components/mpmt-texto-formatado/mpmt-texto-formatado.module';
import { AnotacoesPessoaisPublicacaoNovoComponent } from './anotacoes-pessoais-publicacao-novo/anotacoes-pessoais-publicacao-novo.component';
import { MpmtArquivoModule } from 'components/mpmt-arquivo/mpmt-arquivo.module';
import { AnotacoesPessoaisPublicacaoEditarComponent } from './anotacoes-pessoais-publicacao-editar/anotacoes-pessoais-publicacao-editar.component';
import { MpmtSelecaoFormModule } from 'components/mpmt-selecao-form/mpmt-selecao-form.module';
import { PublicacoesService } from './publicacoes/modal-publicacoes/modal-publicacoes.component.service';
import { ModalPublicacoesComponent } from './publicacoes/modal-publicacoes/modal-publicacoes.component';
import { MpmtListagemSelecaoModule } from 'components/mpmt-listagens/mpmt-listagem-selecao/mpmt-listagem-selecao.module';
import { MpmtFormAutocompleteModule } from 'components/mpmt-form-autocomplete/mpmt-form-autocomplete.module';
import { MpmtFormMultiselecaoServidoresModule } from 'components/mpmt-form-multiselecao-servidores/mpmt-form-multiselecao-servidores.module';
import { MpmtFormMultiselecaoModule } from 'components/mpmt-form-multiselecao/mpmt-form-multiselecao.module';

const ROUTES: Route[] = [...anotacoesPessoaisRoute];

const DECLARATIONS = [
    ModalPublicacoesComponent,
    AnotacoesPessoaisListagemComponent,
    AnotacoesPessoaisPublicacoesComponent,
    AnotacoesPessoaisNovoComponent,
    AnotacoesPessoaisEditarComponent,
    AnotacoesPessoaisVisualizarComponent,
    AnotacoesPessoaisPublicacaoNovoComponent,
    AnotacoesPessoaisPublicacaoEditarComponent,
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [
        AnotacoesPessoaisListagemService,
        AnotacoesPessoaisPublicacoesService,
        PublicacoesService,
    ],
    imports: [
        MpmtFormMultiselecaoModule,
        MpmtFormMultiselecaoServidoresModule,
        MpmtFormAutocompleteModule,
        MpmtListagemSelecaoModule,
        MpmtSelecaoFormModule,
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MaterialModule,
        MpmtListagemModule,
        MpmtListagem2Module,
        MpmtBotaoModule,
        MpmtSelecaoModule,
        MpmtPicklistModule,
        MatTreeModule,
        MatButtonModule,
        MatIconModule,
        FuseDrawerModule,
        MpmtPaginaTituloModule,
        RouterModule.forChild(ROUTES),
        MpmtSelecaoIconesModule,
        MpmtPicklistPaginadoApiModule,
        CKEditorModule,
        MpmtTextoFormatadoModule,
        MpmtArquivoModule,
    ],
    exports: [],
})
export class AnotacoesPessoaisModule {}
