import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { AtualizacaoCadastralEmailComponent } from './atualizacao-cadastral-email.component';
import { MaterialModule } from 'shared/material/material.module';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MpmtBotaoModule } from 'components/mpmt-botao/mpmt-botao.module';

@NgModule({
    declarations: [AtualizacaoCadastralEmailComponent],
    exports: [AtualizacaoCadastralEmailComponent],
    providers: [
        AtualizacaoCadastralEmailComponent,
        { provide: MAT_DIALOG_DATA, useValue: {} },
    ],
    imports: [
        CommonModule,
        FormsModule,
        MaterialModule,
        FormsModule,
        ReactiveFormsModule,
        MpmtBotaoModule,
    ],
})
export class AtualizacaoCadastralEmailModule {}
