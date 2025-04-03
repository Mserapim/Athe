import { NgModule } from '@angular/core';
import { VdfPlantoesService } from './vdf-plantoes.service';
import { VdfPlantoesComponent } from './vdf-plantoes.component';
import { VdfPlantoesRoute } from './vdf-plantoes.route';
import { Route, RouterModule } from '@angular/router';
import { MpmtListagem2Module } from 'components/mpmt-listagem2/mpmt-listagem2.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutModule } from 'layout/layout.module';
import { CommonModule } from '@angular/common';
import { MpmtSelecaoModule } from 'components/mpmt-selecao/mpmt-selecao.module';
import { MpmtChipsAutocompleteModule } from 'components/mpmt-chips-autocomplete/mpmt-chips-autocomplete.module';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';

const route: Route[] = [...VdfPlantoesRoute];

@NgModule({
    declarations: [VdfPlantoesComponent],
    providers: [VdfPlantoesService],
    imports: [
        CommonModule,
        LayoutModule,
        FormsModule,
        MaterialModule,
        ReactiveFormsModule,
        MpmtChipsAutocompleteModule,
        MpmtListagem2Module,
        MpmtSelecaoModule,
        MpmtBotaoModule,
        RouterModule.forChild(route),
    ],
})
export class VdfPlantoesModule {}
