import { Component, Inject, Input, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiAssinadorSuite } from 'api/core/api-core-assinador.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';


class MpmtAssinadorComponentData {
    
    titulo?: string;
    onClose?: Function;
}


@Component({
    selector: 'mpmt-assinador',
    templateUrl: './mpmt-assinador.component.html',
    standalone: false
})
export class MpmtAssinadorComponent extends MpmtFormularioComponent<MpmtAssinadorComponentData> {

    protected titulo: string = "Assinador"

    protected formulario = new FormGroup({
        usuario: new FormControl<string>(null, [Validators.required]),
        senha: new FormControl<string>(null, [Validators.required]),
    });
    
    protected get formularioValido() {
        return this.formulario.valid;
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: MpmtAssinadorComponentData,
        protected dialogRef: MatDialogRef<MpmtAssinadorComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
        if (this.data.titulo){
            this.titulo = this.data.titulo;
        }
    }

    ngOnInit() {
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { usuario, senha } = this.formulario.value;

        try {
            const result = await apiAssinadorSuite({
                usuario: usuario,
                senha: senha,
            });

            this.fecharFormulario();
            this.data?.onClose({ usuario, result });

        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }

    }
}
