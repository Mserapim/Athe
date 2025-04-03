import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { AutoCompleteModule } from 'primeng/autocomplete'; 
import { MessageModule } from 'primeng/message';
import { MpmtFormBaseModule } from 'components/mpmt-form-base/mpmt-form-base.module';
import { MultiSelectModule } from 'primeng/multiselect';
import { CheckboxModule } from 'primeng/checkbox';
import { MpmtFormMultiselecaoServidoresComponent } from './mpmt-form-multiselecao-servidores.component';
import { MpmtFormMultiselecaoModule } from 'components/mpmt-form-multiselecao/mpmt-form-multiselecao.module';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
const DECLARATIONS = [MpmtFormMultiselecaoServidoresComponent];

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
        CheckboxModule,
        MpmtFormMultiselecaoModule,
        ToggleSwitchModule
    ],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
})
export class MpmtFormMultiselecaoServidoresModule {}
