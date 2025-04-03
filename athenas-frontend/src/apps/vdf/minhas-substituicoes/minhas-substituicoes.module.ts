import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MinhasSubstituicoesRoute } from './minhas-substituicoes.route';
import { MinhasSubstituicoesComponent } from './minhas-substituicoes.component';
import { MaterialModule } from 'shared/material/material.module';

const route: Route[] = [...MinhasSubstituicoesRoute];

@NgModule({
    declarations: [MinhasSubstituicoesComponent],
    exports: [MinhasSubstituicoesComponent],
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
export class VdfMinhasSubstituicoesModule {}
