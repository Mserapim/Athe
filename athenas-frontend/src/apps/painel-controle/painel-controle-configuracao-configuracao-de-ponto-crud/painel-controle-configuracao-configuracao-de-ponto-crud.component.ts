import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleConfigPontoCriar, apiPainelControleControleConfigPontoDetail, apiPainelControleControleConfigPontoEditar, apiPainelControleControleConfigPontoApagar } from 'api/painel-controle/api-painel-controle-configuracao-configuracao-de-ponto.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleGrupConfigPontoData {
    pk: number;
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-configuracao-configuracao-de-ponto-crud',
    templateUrl: 'painel-controle-configuracao-configuracao-de-ponto-crud.component.html',
    standalone: false
})
export class PainelControleConfigPontoCRUDComponent extends MpmtFormularioComponent<PainelControleGrupConfigPontoData> {
    protected formulario = new FormGroup({
        place: new FormControl<string>('', [Validators.required]),
        prosecution: new FormControl<string>('', [Validators.required]),
        network: new FormControl<string>('', [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleGrupConfigPontoData,
        protected dialogRef: MatDialogRef<PainelControleGrupConfigPontoData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        this.carregarDados();
    }

    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    async carregarDados() {
        if (this.data.pk != null) {
            const results = await apiPainelControleControleConfigPontoDetail({ id: this.data.pk });
            this.formulario.get('place')?.setValue(results.place);
            this.formulario.get('prosecution')?.setValue(results.prosecution);
            this.formulario.get('network')?.setValue(results.network);
        }
    }

    controlarTitulo() {
        if (this.data.pk != null) {
            return 'Editar Configuração de Ponto'
        }
        return 'Novo Configuração de Ponto'
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { place, prosecution, network } = this.formulario.value;

        try {
            if (this.data.pk != null){
                const id = this.data.pk
                const {} = await apiPainelControleControleConfigPontoEditar({
                    id,
                    place,
                    prosecution,
                    network
                });
            } else {
                const {} = await apiPainelControleControleConfigPontoCriar({
                    place,
                    prosecution,
                    network
                });
            }
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar a configuração. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

}
