import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MpmtFormMultiselecaoComponent } from './mpmt-form-multiselecao.component';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { MessageModule } from 'primeng/message';
import { MpmtFormBaseModule } from 'components/mpmt-form-base/mpmt-form-base.module';
import { MultiSelectModule } from 'primeng/multiselect';
import { CheckboxModule } from 'primeng/checkbox';

const DECLARATIONS = [MpmtFormMultiselecaoComponent];

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        LayoutModule,
        LayoutNavegacaoModule, 
        FuseLoadingBarModule,
        AutoCompleteModule,
        MessageModule,
        MpmtFormBaseModule,
        MultiSelectModule,
        ReactiveFormsModule,
        CheckboxModule
    ],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
})
export class MpmtFormMultiselecaoModule {}
