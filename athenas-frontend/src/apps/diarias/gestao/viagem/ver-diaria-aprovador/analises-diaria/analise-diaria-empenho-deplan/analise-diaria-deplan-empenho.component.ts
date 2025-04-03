import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBeneficiarioAnaliseDeplanCriar } from 'api/diarias/analise-beneficiario/api-analise-deplan-empenho.service';
import { apiMoverFluxoBenecificarios } from 'api/diarias/analise-beneficiario/api-mover-fluxo-beneficiario.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariaAnaliseDeplanEmpenhoData {
    beneficiario: number;
    viagem: number;
    exibirEncaminhar: boolean;
    onClose?: Function;
}

@Component({
    selector: 'analise-diaria-deplan-empenho',
    templateUrl: 'analise-diaria-deplan-empenho.component.html',
    standalone: false
})
export class DiariaAnaliseDeplanEmpenhoComponent extends MpmtFormularioComponent<DiariaAnaliseDeplanEmpenhoData> implements OnInit{
    anexos: any[] = []

    protected formulario = new FormGroup({
        numeroEmpenho: new FormControl<number>(null, [Validators.required]),
    });

    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariaAnaliseDeplanEmpenhoData,
        protected dialogRef: MatDialogRef<DiariaAnaliseDeplanEmpenhoData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { numeroEmpenho } = this.formulario.value;
        const anexos = this.anexos

        try {
            await apiBeneficiarioAnaliseDeplanCriar({
                viagem: this.data.viagem,
                beneficiario: this.data.beneficiario,
                numero_empenho: numeroEmpenho,
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

    protected async encaminharDG (){
        const fluxoDG = 48 // Fluxo: Liberação de empenho - DG
        try {
            const response = await apiMoverFluxoBenecificarios({
                beneficiarios:[this.data.beneficiario],
                fluxoEspecifico:fluxoDG,
            })

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (error) {
            console.error('Erro ao salvar', error);
        }
    }
}
