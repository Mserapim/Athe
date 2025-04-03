import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MessageModule } from 'primeng/message';
import { DatePickerModule } from 'primeng/datepicker';
import { MpmtFormBaseComponent } from './mpmt-form-base.component';


const DECLARATIONS = [MpmtFormBaseComponent];

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
    ],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
})
export class MpmtFormBaseModule {}
