import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RequestNewExercicioCumulativoModule } from './request-new-exercicio-cumulativo/request-new-exercicio-cumulativo.module';
import { MaterialModule } from 'shared/material/material.module';
import {RequestNewAuxilioCrecheIrModule} from "./request-new-auxilio-creche-ir/request-new-auxilio-creche-ir.module";

const modules = [RequestNewExercicioCumulativoModule, RequestNewAuxilioCrecheIrModule];

@NgModule({
    declarations: [],
    exports: [modules],
    providers: [],
    imports: [
        modules,
        CommonModule,
        FormsModule,
        LayoutModule,
        FormsModule,
        ReactiveFormsModule,
        MaterialModule,
    ],
})
export class VdfRequestModule {}
