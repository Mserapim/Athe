import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MessageModule } from 'primeng/message';
import { DatePickerModule } from 'primeng/datepicker';
import { MpmtFormAnexoComponent } from './mpmt-form-anexo.component';
import { RadioButtonModule } from 'primeng/radiobutton';
import { MpmtFormBaseModule } from 'components/mpmt-form-base/mpmt-form-base.module';
import { ButtonModule } from 'primeng/button';
import { FileUploadModule } from 'primeng/fileupload';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TooltipModule } from 'primeng/tooltip';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

const DECLARATIONS = [MpmtFormAnexoComponent];

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        LayoutModule,
        LayoutNavegacaoModule,
        FuseLoadingBarModule,
        DatePickerModule,
        MessageModule,
        RadioButtonModule,
        MpmtFormBaseModule,
        ButtonModule,
        FileUploadModule,
        ProgressSpinnerModule,
        TooltipModule,
        ToastModule
    ],
    providers: [MessageService],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
})
export class MpmtFormAnexoModule { }
