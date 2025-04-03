import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpBotaoDownloadPdfComponent } from './mp-botao-download-pdf.component';

const DECLARATIONS = [MpBotaoDownloadPdfComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: [],
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        ReactiveFormsModule,
    ],
})
export class MpBotaoDownloadPdfModule {}
