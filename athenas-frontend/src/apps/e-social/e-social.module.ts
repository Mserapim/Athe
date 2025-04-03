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

import { ESocialRoute } from './e-social.route';

import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import {ESocialItensTabelaComponent} from "./itens-tabela/e-social-itens-tabela.component";
import {ESocialItensTabelaService} from "./itens-tabela/e-social-itens-tabela.service";
import {
    ItemTabelaCriarDialogComponent
} from "./itens-tabela/components/item-tabela-criar-dialog/item-tabela-criar-dialog.component";
import {MpmtChipsAutocompleteModule} from "../../components/mpmt-chips-autocomplete/mpmt-chips-autocomplete.module";
import {
    ItemTabelaEditarDialogComponent
} from "./itens-tabela/components/item-tabela-editar-dialog/item-tabela-editar-dialog.component";
import { MatMomentDateModule, MAT_MOMENT_DATE_ADAPTER_OPTIONS } from '@angular/material-moment-adapter';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MAT_DATE_FORMATS, DateAdapter, MAT_DATE_LOCALE } from '@angular/material/core';
import { MomentDateAdapter } from '@angular/material-moment-adapter';
import {MpmtListagem2AccordionModule} from "../../components/mpmt-listagem2-accordion/mpmt-listagem2-accordion.module";
import {ESocialQualificacaoCadastralService} from "./qualificacao-cadastral/e-social-qualificacao-cadastral.service";
import {
    ESocialQualificacaoCadastralComponent
} from "./qualificacao-cadastral/e-social-qualificacao-cadastral.component";
import {
    QualificacaoCadastralGerarArquivoDialogComponent
} from "./qualificacao-cadastral/components/qualificacao-cadastral-gerar-arquivo-dialog/qualificacao-cadastral-gerar-arquivo-dialog.component";
import {
    QualificacaoCadastralConfirmarQualificacaoDialogComponent
} from "./qualificacao-cadastral/components/qualificacao-cadastral-confirmar-qualificacao-dialog/qualificacao-cadastral-confirmar-qualificacao-dialog.component";
import {MpmtFileUpdateModule} from "../../components/mpmt-file-update/mpmt-file-update.module";
import {ESocialConfiguracoesComponent} from "./configuracoes/e-social-configuracoes.component";
import {ESocialConfiguracoesService} from "./configuracoes/e-social-configuracoes.service";
import {
    ConfiguracaoCriarDialogComponent
} from "./configuracoes/components/configuracao-criar-dialog/configuracao-criar-dialog.component";
import {
    VincularServidoresDialogComponent
} from "./configuracoes/components/vincular-servidores-dialog/vincular-servidores-dialog.component";
import {
    VincularServidoresDialogService
} from "./configuracoes/components/vincular-servidores-dialog/vincular-servidores-dialog.service";
import {
    MpmtPicklistPaginadoApiModule
} from "../../components/mpmt-picklist-paginado-api/mpmt-picklist-paginado-api.module";
import {
    ConfiguracaoEditarDialogComponent
} from "./configuracoes/components/configuracao-editar-dialog/configuracao-editar-dialog.component";
import {
    AtualizarCertificadoDialogComponent
} from "./configuracoes/components/atualizar-certificado-dialog/atualizar-certificado-dialog.component";

const DATE_FORMATS = {
    parse: {
        dateInput: 'DD/MM/YYYY',
    },
    display: {
        dateInput: 'DD/MM/YYYY',
        monthYearLabel: 'MMM YYYY',
        dateA11yLabel: 'DD/MM/YYYY',
        monthYearA11yLabel: 'MMMM YYYY',
    },
};

const ROUTES: Route[] = [...ESocialRoute];

const DECLARATIONS = [
    ESocialItensTabelaComponent,
    ItemTabelaCriarDialogComponent,
    ItemTabelaEditarDialogComponent,
    ESocialQualificacaoCadastralComponent,
    QualificacaoCadastralGerarArquivoDialogComponent,
    QualificacaoCadastralConfirmarQualificacaoDialogComponent,
    ESocialConfiguracoesComponent,
    ConfiguracaoCriarDialogComponent,
    VincularServidoresDialogComponent,
    ConfiguracaoEditarDialogComponent,
    AtualizarCertificadoDialogComponent
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [ESocialItensTabelaService, ESocialQualificacaoCadastralService, ESocialConfiguracoesService,
        VincularServidoresDialogService,
        { provide: DateAdapter, useClass: MomentDateAdapter, deps: [MAT_DATE_LOCALE, MAT_MOMENT_DATE_ADAPTER_OPTIONS] },
        { provide: MAT_DATE_FORMATS, useValue: DATE_FORMATS }],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MaterialModule,
        MpmtListagemModule,
        MpmtBotaoModule,
        MpmtSelecaoModule,
        MpmtPicklistModule,
        MatTreeModule,
        MatButtonModule,
        MpmtListagem2Module,
        MatIconModule,
        RouterModule.forChild(ROUTES),
        MpmtChipsAutocompleteModule,
        MatDatepickerModule,
        MatMomentDateModule,
        MpmtListagem2AccordionModule,
        MpmtFileUpdateModule,
        MpmtPicklistPaginadoApiModule
    ],
    exports: [],
})
export class ESocialModule {}
