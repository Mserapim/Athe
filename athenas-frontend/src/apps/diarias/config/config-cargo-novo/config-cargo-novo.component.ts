import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigCargoCriar } from 'api/diarias/config/api-diarias-config-cargo-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariasConfigCargoNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'config-cargo-novo',
    templateUrl: 'config-cargo-novo.component.html',
    standalone: false
})
export class DiariasConfigCargoNovoComponent extends MpmtFormularioComponent<DiariasConfigCargoNovoComponentData> {
    protected formulario = new FormGroup({
        nome: new FormControl<string>('', [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigCargoNovoComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigCargoNovoComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome } = this.formulario.value;

        try {
            const {} = await apiDiariasConfigCargoCriar({
                nome,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o cargo. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }
}
