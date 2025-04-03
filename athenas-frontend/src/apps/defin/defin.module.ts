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

import { definRoute } from './defin.route';

import { ColaboradorEventualComponent } from './colaboradores-eventuais/colaboradores-eventuais.component';
import { ColaboradorEventualService } from './colaboradores-eventuais/colaboradores-eventuais.service';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { MpmtListagem2AccordionModule } from 'components/mpmt-listagem2-accordion/mpmt-listagem2-accordion.module';
import { ColaboradorEventualModalComponent } from './colaboradores-eventuais/modal-colaborador-eventual/modal-colaborador-eventual.component';
import { LayoutPadraoModalModule } from 'layout/mpmt-modal/layout-padrao-modal.module';
import { MpmtListagemSelecaoModule } from 'components/mpmt-listagens/mpmt-listagem-selecao/mpmt-listagem-selecao.module';
import { MpmtSelecaoFormModule } from 'components/mpmt-selecao-form/mpmt-selecao-form.module';
import { MatExpansionModule } from '@angular/material/expansion';
import { MpmtPaginaListagemModule } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.module';
import { CoreModule } from 'apps/core/core.module';


import { TableModule } from 'primeng/table';
import { PagamentoColaboradorEventualModalComponent } from './colaboradores-eventuais/modal-pagamento-colaborador-eventual/modal-pagamento-colaborador-eventual.component';
import { MpmtFormAutocompleteModule } from 'components/mpmt-form-autocomplete/mpmt-form-autocomplete.module';
import { ConfirmDialogModule } from 'primeng/confirmdialog';



const ROUTES: Route[] = [...definRoute];

const DECLARATIONS = [
    ColaboradorEventualComponent,
    ColaboradorEventualModalComponent,
    PagamentoColaboradorEventualModalComponent,
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [

        ColaboradorEventualService
    ],
    imports: [
        ConfirmDialogModule, 
        MpmtFormAutocompleteModule,
        TableModule,
        CoreModule,
        MpmtPaginaListagemModule,
        MatExpansionModule,
        MpmtListagemSelecaoModule,
        MpmtSelecaoFormModule,
        MpmtSelecaoModule,
        LayoutPadraoModalModule,
        MpmtListagem2AccordionModule,
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
    ],
    exports: [],
})
export class DefinModule { }
