import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MaterialModule } from 'shared/material/material.module';
import { LayoutModule } from 'layout/layout.module';
import { LayoutNavegacaoModule } from 'layout/layout-navegacao/layout-navegacao.module';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { MessageModule } from 'primeng/message';
import { InputTextModule } from 'primeng/inputtext';
import { InputGroupModule } from 'primeng/inputgroup';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';
import { MpmtFormTextoComponent } from './mpmt-form-texto.component';
import { MpmtFormBaseModule } from 'components/mpmt-form-base/mpmt-form-base.module';

const DECLARATIONS = [MpmtFormTextoComponent];

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        LayoutNavegacaoModule,
        FuseLoadingBarModule,
        MessageModule,
        InputTextModule,
        InputGroupModule,
        InputGroupAddonModule,
        MpmtFormBaseModule
    ],
    declarations: DECLARATIONS,
    exports: DECLARATIONS,
    providers: [],
})
export class MpmtFormTextoModule {}
