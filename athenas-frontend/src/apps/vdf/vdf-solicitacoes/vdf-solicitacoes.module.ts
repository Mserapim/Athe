import { NgModule } from '@angular/core';
import { VdfSolicitacoesService } from './vdf-solicitacoes.service';
import { VdfSolicitacoesComponent } from './vdf-solicitacoes.component';
import { VdfSolicitacoesRoute } from './vdf-solicitacoes.route';
import { Route, RouterModule } from '@angular/router';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutModule } from 'layout/layout.module';
import { CommonModule } from '@angular/common';

const route: Route[] = [...VdfSolicitacoesRoute];

@NgModule({
    declarations: [VdfSolicitacoesComponent],
    providers: [VdfSolicitacoesService],
    imports: [
        CommonModule,
        LayoutModule,
        FormsModule,
        MaterialModule,
        ReactiveFormsModule,
        MpmtListagem2Module,
        RouterModule.forChild(route),
    ],
})
export class VdfSolicitacoesModule {}
