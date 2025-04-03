import { NgModule } from '@angular/core';
import { VdfAprovacoesService } from './vdf-aprovacoes.service';
import { VdfAprovacoesComponent } from './vdf-aprovacoes.component';
import { VdfAprovacoesRoute } from './vdf-aprovacoes.route';
import { Route, RouterModule } from '@angular/router';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutModule } from 'layout/layout.module';
import { CommonModule } from '@angular/common';

const route: Route[] = [...VdfAprovacoesRoute];

@NgModule({
    declarations: [VdfAprovacoesComponent],
    providers: [VdfAprovacoesService],
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
export class VdfAprovacoesModule {}