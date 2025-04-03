import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtAbasComponent } from './mpmt-abas.component';

const DECLARATIONS = [MpmtAbasComponent, ];

@NgModule({
    declarations: DECLARATIONS,
    providers: DECLARATIONS,
    exports: DECLARATIONS,
    imports: [

        CommonModule,
        MaterialModule,
    ],
})
export class MpmtAbasModule {}

