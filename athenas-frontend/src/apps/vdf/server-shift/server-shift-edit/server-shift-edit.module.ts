import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { ServerShiftEditComponent } from './server-shift-edit.component';
import { MaterialModule } from 'shared/material/material.module';
import { AutocompleteLibModule } from 'angular-ng-autocomplete';
import {MpmtBotaoModule} from "../../../../components/mpmt-botao/mpmt-botao.module";

const route: Route[] = [];

@NgModule({
    declarations: [ServerShiftEditComponent],
    exports: [ServerShiftEditComponent],
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        ReactiveFormsModule,
        MatIconModule,
        MaterialModule,
        AutocompleteLibModule,
        MpmtBotaoModule,
        RouterModule.forChild(route),
    ],
})
export class VdfServerShiftEditModule {}
