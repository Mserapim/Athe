import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Route, RouterModule } from '@angular/router';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';
import { coreRoute } from './core.route';
import { MpmtAssinadorComponent } from './mpmt-assinador/mpmt-assinador.component';
import { MatInputModule } from '@angular/material/input';
import { LayoutModule } from 'layout/layout.module';
import { MatFormFieldModule } from '@angular/material/form-field';
import { EnderecoListagemComponent } from './cadastros-genericos/endereco/endereco-listagem.component';
import { EnderecoService } from './cadastros-genericos/endereco/endereco-listagem.service';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { MpmtCabecalhoListagemModule } from 'components/mpmt-listagens/mpmt-cabecalho-listagem/mpmt-cabecalho-listagem.module';
import { LayoutPadraoModalModule } from 'layout/mpmt-modal/layout-padrao-modal.module';
import { EnderecoModalComponent } from './cadastros-genericos/endereco/modal-endereco/modal-endereco.component';
import { MpmtSelecaoFormModule } from 'components/mpmt-selecao-form/mpmt-selecao-form.module';
import { TelefoneListagemComponent } from './cadastros-genericos/telefone/telefone-listagem.component';
import { TelefoneModalComponent } from './cadastros-genericos/telefone/modal-telefone/modal-telefone.component';
import { TelefoneService } from './cadastros-genericos/telefone/telefone-listagem.service';


const ROUTES: Route[] = [...coreRoute];

const DECLARATIONS = [
    MpmtAssinadorComponent,
    EnderecoListagemComponent,
    EnderecoModalComponent,
    TelefoneListagemComponent,
    TelefoneModalComponent,
];

@NgModule({
    declarations: DECLARATIONS,
    providers: [
        EnderecoService,
        TelefoneService,
    ],
    imports: [
        MpmtSelecaoFormModule,
        LayoutPadraoModalModule,
        MatFormFieldModule,
        MpmtListagem2Module,
        MpmtCabecalhoListagemModule,
        MpmtBotaoModule,
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        ReactiveFormsModule,
        RouterModule.forChild(ROUTES),
    ],
    exports: [
        MpmtAssinadorComponent,
        EnderecoListagemComponent,
        TelefoneListagemComponent,
    ],
})
export class CoreModule {}
