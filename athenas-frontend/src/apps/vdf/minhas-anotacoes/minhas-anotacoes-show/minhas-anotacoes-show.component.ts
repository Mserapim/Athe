import { Component, Inject, OnInit } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { printDate } from 'utils/print-date';

@Component({
    selector: 'minhas-anotacoes-show',
    templateUrl: 'minhas-anotacoes-show.html',
    standalone: false
})
export class MinhasAnotacoesShow implements OnInit {
    anoatacao: any = null;

    printDate = printDate;

    constructor(
        private dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA) public data: any
    ) {}

    ngOnInit() {
        this.anoatacao = this.data.element;
    }

    fechar(): void {
        this.dialog.closeAll();
    }
}
