import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBeneficiarioAnaliseDefinCriar } from 'api/diarias/analise-beneficiario/api-analise-defin-nota-liquidacao.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariaAnaliseDefinNotaData {
    beneficiario: number;
    viagem: number;
    onClose?: Function;
}

@Component({
    selector: 'analise-diaria-defin-nota-liquidacao',
    templateUrl: 'analise-defin-nota-liquidacao.component.html',
    standalone: false
})
export class DiariaAnaliseDefinNotaComponent extends MpmtFormularioComponent<DiariaAnaliseDefinNotaData> implements OnInit{
    anexos: any[] = []

    protected formulario = new FormGroup({
        numeroNotaLiquidacao: new FormControl<number>(null),
    });

    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariaAnaliseDefinNotaData,
        protected dialogRef: MatDialogRef<DiariaAnaliseDefinNotaData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { numeroNotaLiquidacao } = this.formulario.value;
        const anexos = this.anexos

        try {
            await apiBeneficiarioAnaliseDefinCriar({
                viagem: this.data.viagem,
                beneficiario: this.data.beneficiario,
                numero_nota_liquidacao: numeroNotaLiquidacao,
                anexos
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar a análise. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    protected get formularioValido() {
        return this.formulario.valid && this.anexos.length > 0;
    }

    protected async receberAnexos(dados: []) {
        this.anexos = dados
    }
}
