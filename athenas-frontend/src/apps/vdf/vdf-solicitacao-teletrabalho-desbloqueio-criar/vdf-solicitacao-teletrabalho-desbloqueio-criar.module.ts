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
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponentRoute } from './vdf-solicitacao-teletrabalho-desbloqueio-criar.route';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponent } from './vdf-solicitacao-teletrabalho-desbloqueio-criar.component';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperComponent } from './vdf-solicitacao-teletrabalho-desbloqueio-criar-stepper/request-new-relatorio-teletrabalho-semestral-criar-stepper.component';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep1Component } from './vdf-solicitacao-teletrabalho-desbloqueio-criar-step1/vdf-solicitacao-teletrabalho-desbloqueio-criar-step1.component';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep2Component } from './vdf-solicitacao-teletrabalho-desbloqueio-criar-step2/vdf-solicitacao-teletrabalho-desbloqueio-criar-step2.component';
import { VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService } from './vdf-solicitacao-teletrabalho-desbloqueio-criar-stepper/request-new-relatorio-teletrabalho-semestral-criar-stepper.service';

const route: Route[] = [
    ...VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponentRoute,
];

@NgModule({
    declarations: [
        VdfSolicitacaoTeletrabalhoDesbloqueioCriarComponent,
        VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperComponent,
        VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep1Component,
        VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep2Component,
    ],
    providers: [
        VdfSolicitacaoTeletrabalhoDesbloqueioCriarStepperService,
        VdfSolicitacaoTeletrabalhoDesbloqueioCriarStep1Component,
    ],
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
        RouterModule.forChild(route),
    ],
})
export class VdfSolicitacaoTeletrabalhoDesbloqueioCriarModule {}
