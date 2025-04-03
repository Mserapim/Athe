import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtCelulaComponent } from './mpmt-celula.component';

const DECLARATIONS = [ MpmtCelulaComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: DECLARATIONS,
    exports: DECLARATIONS,
    imports: [


        CommonModule,
        LayoutModule,
        MaterialModule,
    ],
})
export class MpmtCelulaModule {}
