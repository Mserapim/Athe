import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MinhasAnotacoesRoute } from './minhas-anotacoes.route';
import { MinhasAnotacoesComponent } from './minhas-anotacoes.component';
import { MaterialModule } from 'shared/material/material.module';
import { MinhasAnotacoesShow } from './minhas-anotacoes-show/minhas-anotacoes-show.component';

const route: Route[] = [...MinhasAnotacoesRoute];

@NgModule({
    declarations: [MinhasAnotacoesComponent, MinhasAnotacoesShow],
    exports: [MinhasAnotacoesComponent],
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        ReactiveFormsModule,
        RouterModule.forChild(route),
    ],
})
export class VdfMinhasAnotacoesModule {}
