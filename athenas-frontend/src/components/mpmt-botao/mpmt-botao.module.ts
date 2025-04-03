import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtBotaoComponent } from './mpmt-botao.component';
import { MpmtDirectivesModule } from 'directives/directives.module';

const DECLARATIONS = [MpmtBotaoComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: [],
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        FormsModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        ReactiveFormsModule,
        MpmtDirectivesModule,
    ],
})
export class MpmtBotaoModule {}
