import { Component, Inject } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { apiRhPvfVendaSubstituicaoIdIndeferir } from 'api/rh/api-rh-pvf-venda-substituicao-id-indeferir.service';

@Component({
    selector: 'request-indeferir-dialog',
    templateUrl: 'request-indeferir-dialog.html',
    standalone: false
})
export class RequestIndeferirDialog {
    observation: string = '';
    message: string;

    constructor(
        private dialogRef: MatDialogRef<RequestIndeferirDialog>,
        private matDialog: MatDialog,
        @Inject(MAT_DIALOG_DATA) public data: any
    ) {}

    fechar(): void {
        this.dialogRef.close();
    }

    public async indeferir(): Promise<void> {
        this.message = null;
        try {
            await apiRhPvfVendaSubstituicaoIdIndeferir({
                itemId: this.data.itemId,
                observation: this.observation,
            });
            this.dialogRef.close();
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }
}
