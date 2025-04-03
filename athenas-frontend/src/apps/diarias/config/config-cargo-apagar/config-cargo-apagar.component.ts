import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigCargoApagar } from 'api/diarias/config/api-diarias-config-cargo-apagar.service ';
import { apiDiariasConfigCargo } from 'api/diarias/config/api-diarias-config-cargo.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariasConfigCargoApagarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'config-cargo-apagar',
    templateUrl: 'config-cargo-apagar.component.html',
    standalone: false
})
export class DiariasConfigCargoApagarComponent extends MpmtFormularioComponent<DiariasConfigCargoApagarComponentData> {
    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        nome: new FormControl<string>('', []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigCargoApagarComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigCargoApagarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id, nome } =
                await apiDiariasConfigCargo({
                    id: this.data.id,
                });

            await this.formulario.patchValue({
                id,
                nome,
            });
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { id, nome } = this.formulario.value;

        try {
            const {} = await apiDiariasConfigCargoApagar({
                id,
                nome,
            });

            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao apagar o cargo. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

}
