import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MpmtFormAutocompleteComponent } from './mpmt-form-autocomplete.component';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { MessageModule } from 'primeng/message';
import { MpmtFormBaseModule } from 'components/mpmt-form-base/mpmt-form-base.module';

const DECLARATIONS = [MpmtFormAutocompleteComponent];

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
        MpmtFormBaseModule
    ],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
})
export class MpmtFormAutocompleteModule {}
