import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MessageModule } from 'primeng/message';
import { DatePickerModule } from 'primeng/datepicker';
import { MpmtFormBotaoSelecaoComponent } from './mpmt-form-botao-selecao.component';
import { RadioButtonModule } from 'primeng/radiobutton';
import { MpmtFormBaseModule } from 'components/mpmt-form-base/mpmt-form-base.module';

const DECLARATIONS = [MpmtFormBotaoSelecaoComponent];

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
        MpmtFormBaseModule
    ],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
})
export class MpmtFormBotaoSelecaoModule {}
