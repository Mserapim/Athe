import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleServicoApagar } from 'api/painel-controle/api-painel-controle-servico-apagar.service';
import { apiPainelControleServico } from 'api/painel-controle/api-painel-controle-servico.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class PainelControleServicoApagarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-servico-apagar',
    templateUrl: 'painel-controle-servico-apagar.component.html',
    standalone: false
})
export class PainelControleServicoApagarComponent extends MpmtFormularioComponent<PainelControleServicoApagarComponentData> {
    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        name: new FormControl<string>('', []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleServicoApagarComponentData,
        protected dialogRef: MatDialogRef<PainelControleServicoApagarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id } =
                await apiPainelControleServico({
                    id: this.data.id,
                });

            await this.formulario.patchValue({
                id,
            });
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os serviços do formulário'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { id, name } = this.formulario.value;

        try {
            const {} = await apiPainelControleServicoApagar({
                id,
            });

            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao apagar o serviço. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

}
