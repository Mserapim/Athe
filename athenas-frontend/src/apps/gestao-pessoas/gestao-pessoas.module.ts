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
import { MpmtTextoFormatadoModule } from 'components/mpmt-texto-formatado/mpmt-texto-formatado.module';
import { MpmtArquivoModule } from 'components/mpmt-arquivo/mpmt-arquivo.module';
import { MpmtSelecaoFormModule } from 'components/mpmt-selecao-form/mpmt-selecao-form.module';
import { MpmtListagemSelecaoModule } from 'components/mpmt-listagens/mpmt-listagem-selecao/mpmt-listagem-selecao.module';
import { gestaoPessoasRoute } from './gestao-pessoas.route';
import { GestaoPessoasGestaoVdfService } from './gestao-pessoas-gestao-vdf/gestao-pessoas-gestao-vdf.service';
import { GestaoPessoasGestaoVdfComponent } from './gestao-pessoas-gestao-vdf/gestao-pessoas-gestao-vdf.component';
import { MpmtPaginaModule } from 'components/mpmt-pagina/mpmt-pagina.module';
import { MpmtPaginaListagemModule } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.module';
import { MultiSelectModule } from 'primeng/multiselect';
import { MpmtFormAutocompleteModule } from 'components/mpmt-form-autocomplete/mpmt-form-autocomplete.module';
import { MpmtFormPeriodoModule } from 'components/mpmt-form-periodo/mpmt-form-periodo.module';
import { MpmtFormBotaoSelecaoModule } from 'components/mpmt-form-botao-selecao/mpmt-form-botao-selecao.module';
import { RadioButtonModule } from 'primeng/radiobutton'; 
import { TableModule } from 'primeng/table';
import { MpmtPaginaDialogoModule } from 'components/mpmt-pagina-dialogo/mpmt-pagina-dialogo.module';
import { GestaoPessoasGestaoVdfVisualizarComponent } from './gestao-pessoas-gestao-visualizar/gestao-pessoas-gestao-vdf-visualizar.component';
import { GestaoPessoasGestaoVdfVisualizarService } from './gestao-pessoas-gestao-visualizar/gestao-pessoas-gestao-vdf-visualizar.service';
import { DialogModule } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';
import { PopoverModule } from 'primeng/popover';
import { MpmtFormAnexoModule } from 'components/mpmt-form-anexo/mpmt-form-anexo.module';
import { MpmtFormMultiselecaoModule } from 'components/mpmt-form-multiselecao/mpmt-form-multiselecao.module';
import { MpmtFormMultiselecaoServidoresModule } from 'components/mpmt-form-multiselecao-servidores/mpmt-form-multiselecao-servidores.module';
import { DynamicDialogModule } from 'primeng/dynamicdialog';
import { MpmtFormTextoModule } from 'components/mpmt-form-texto/mpmt-form-texto.module';
import { GestorCargosService } from './gestor-cargos/gestor-cargos.service';
import { GestorCargosComponent } from './gestor-cargos/gestor-cargos.component';
const ROUTES: Route[] = [...gestaoPessoasRoute];

const DECLARATIONS = [
  GestaoPessoasGestaoVdfComponent,
  GestaoPessoasGestaoVdfVisualizarComponent,
  GestorCargosComponent,
];

@NgModule({ 
    declarations: DECLARATIONS,
    providers: [
      GestaoPessoasGestaoVdfService,
      GestaoPessoasGestaoVdfVisualizarService,
      GestaoPessoasGestaoVdfVisualizarComponent,
      GestorCargosService,
    ],
    imports: [
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
        MpmtSelecaoIconesModule,
        MpmtPicklistPaginadoApiModule,
        MpmtTextoFormatadoModule,
        MpmtArquivoModule,
        RouterModule.forChild(ROUTES),
        MultiSelectModule,
        MpmtPaginaModule,
        MpmtPaginaListagemModule,
        MpmtFormAutocompleteModule,
        MpmtFormPeriodoModule,
        MpmtFormBotaoSelecaoModule,
        MpmtPaginaDialogoModule,
        RadioButtonModule,
        ButtonModule,
        TableModule,
        DialogModule,
        PopoverModule,
        MpmtFormAnexoModule, 
        MpmtFormMultiselecaoModule,
        MpmtFormMultiselecaoServidoresModule,
        DynamicDialogModule,
        MpmtFormTextoModule 
    ],
    exports: [],
}) 
export class GestaoPessoasModule {}
