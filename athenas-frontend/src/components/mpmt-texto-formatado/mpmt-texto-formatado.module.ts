import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtTextoFormatadoComponent } from './mpmt-texto-formatado.component';
import { CKEditorModule } from '@ckeditor/ckeditor5-angular';

const DECLARATIONS = [MpmtTextoFormatadoComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: DECLARATIONS,
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        ReactiveFormsModule,
        CKEditorModule,
    ],
})
export class MpmtTextoFormatadoModule {}
