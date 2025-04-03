import { Component, Inject, Input, OnInit, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
    selector: 'mpmt-formulario',
    templateUrl: './mpmt-formulario.component.html',
    standalone: false
})
export class MpmtFormularioComponent<TData extends any> implements OnInit {
    protected formulario = new FormGroup<any>({});
    protected formularioPadrao: any = {};

    constructor(
        @Inject(MAT_DIALOG_DATA) protected data: TData,
        protected snackBar: MatSnackBar,
        protected dialogRef: MatDialogRef<TData>
    ) {}

    ngOnInit() {
        this.formularioPadrao = this.formulario.value;
        this.resetarFormulario();
    }

    protected resetarFormulario() {
        this.formulario.patchValue(this.formularioPadrao);
    }

    protected async confirmarFormulario(event?: Event) {}

    protected fecharFormulario() {
        this.dialogRef.close();
    }

    protected get formularioValido() {
        return this.formulario.valid;
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected exibirErro(e: any) {
        const detalheErro = e?.response?.data?.message || '';
        const texto = detalheErro || `Ocorreu um erro inesperado ao salvar`;
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }
}
