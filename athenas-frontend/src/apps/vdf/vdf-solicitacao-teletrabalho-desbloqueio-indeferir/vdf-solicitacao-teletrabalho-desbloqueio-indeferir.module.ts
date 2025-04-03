import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../request/components/request-stepper/request-stepper.module';
import { RequestShowModule } from '../request/components/request-show/request-show.module';
import { MpmtArquivoModule } from 'components/mpmt-arquivo/mpmt-arquivo.module';
import { VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirComponent } from './vdf-solicitacao-teletrabalho-desbloqueio-indeferir.component';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';

const route: Route[] = [];

@NgModule({
    declarations: [VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirComponent],
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RequestStepperModule,
        RequestShowModule,
        MpmtArquivoModule,
        MpmtBotaoModule,
        RouterModule.forChild(route),
    ],
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioIndeferirModule {}
