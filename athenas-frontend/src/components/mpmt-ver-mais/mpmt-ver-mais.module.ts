import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MpmtVerMaisComponent } from './mpmt-ver-mais.component';
import { MaterialModule } from 'shared/material/material.module';  // Verifique se está correto
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogActions } from '@angular/material/dialog';
import { LayoutPadraoModalModule } from "../../layout/mpmt-modal/layout-padrao-modal.module";

const DECLARATIONS = [MpmtVerMaisComponent];


@NgModule({
    declarations: DECLARATIONS,
    providers: DECLARATIONS,
    exports: DECLARATIONS,
    imports: [
    CommonModule,
    MaterialModule,
    MatListModule,
    MatDividerModule,
    MatDialogActions,
    MaterialModule,
    MatIconModule,
    LayoutPadraoModalModule,
],
})
export class MpmtVerMaisModule {}
