import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
    selector: 'mpmt-ver-mais',
    templateUrl: './mpmt-ver-mais.component.html',
    standalone: false,
})

export class MpmtVerMaisComponent {
    constructor(
        public dialogRef: MatDialogRef<MpmtVerMaisComponent>,
        @Inject(MAT_DIALOG_DATA) public data: { titulo: string, conteudo: string }
    ) {}

    fechar(): void {
        this.dialogRef.close();
    }
}
