import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigValorApagar } from 'api/diarias/config/api-diarias-config-valor-apagar.service';
import { apiDiariasConfigValor } from 'api/diarias/config/api-diarias-config-valor.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariasConfigValorApagarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'config-valor-apagar',
    templateUrl: 'config-valor-apagar.component.html',
    standalone: false
})
export class DiariasConfigValorApagarComponent extends MpmtFormularioComponent<DiariasConfigValorApagarComponentData> {
    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        nome: new FormControl<string>('', []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigValorApagarComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigValorApagarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id } =
                await apiDiariasConfigValor({
                    id: this.data.id,
                });

            await this.formulario.patchValue({
                id,
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
            const {} = await apiDiariasConfigValorApagar({
                id,
            });

            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao apagar o valor. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

}
