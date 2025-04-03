import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleClasscodeApagar } from 'api/painel-controle/api-painel-controle-classcode-apagar.service';
import { apiPainelControleClasscode } from 'api/painel-controle/api-painel-controle-classcode.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class PainelControleClasscodeApagarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-classcode-apagar',
    templateUrl: 'painel-controle-classcode-apagar.component.html',
    standalone: false
})
export class PainelControleClasscodeApagarComponent extends MpmtFormularioComponent<PainelControleClasscodeApagarComponentData> {
    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleClasscodeApagarComponentData,
        protected dialogRef: MatDialogRef<PainelControleClasscodeApagarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id } =
                await apiPainelControleClasscode({
                    id: this.data.id,
                });

            await this.formulario.patchValue({
                id,
            });
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os dados do formulário'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { id } = this.formulario.value;

        try {
            const {} = await apiPainelControleClasscodeApagar({
                id,
            });

            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao apagar o classcode. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

}
