import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBenecificarioAnaliseQuantidadeDiarias } from 'api/diarias/aprovacoes-beneficiario/analise-quantidade-diarias.service';
import { apiBenecificarioInformacaoEAprovacao } from 'api/diarias/aprovacoes-beneficiario/informacao-e-aprovacao.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class AprovarEditarNumeroDiariasData {
    beneficiario: number;
    titulo: string;
    excedente: boolean;
    possuiExcedente: boolean;
    qtdTotalDiarias: number;
    qtdTotalDiariasDeferidas: number;
    encaminhar: boolean;
    reanalise: boolean;
    onClose?: Function;
}

@Component({
    selector: 'aprovar-e-alterar-numero-diarias',
    templateUrl: 'aprovar-e-alterar-numero-diarias.component.html',
    standalone: false
})
export class AprovarEditarNumeroDiariasComponent extends MpmtFormularioComponent<AprovarEditarNumeroDiariasData> implements OnInit{

    protected formulario = new FormGroup({
        quantidadeTotal: new FormControl<number>(this.data.qtdTotalDiarias),
        quantidadeDeferida: new FormControl<number>(this.data.qtdTotalDiarias, [Validators.required]),
        analise: new FormControl<string>(''),
        feedback: new FormControl<string>(null),
    });

    
    ngOnInit() {
        super.ngOnInit();

        if (this.data.excedente || this.data.possuiExcedente) {
            this.formulario.controls['quantidadeDeferida'].disable();
        }
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AprovarEditarNumeroDiariasData,
        protected dialogRef: MatDialogRef<AprovarEditarNumeroDiariasData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    async irAnalisar(fluxoEspecifico?: number) {
        const feedbackControl = this.formulario.get('feedback');

        if (!fluxoEspecifico) {
            feedbackControl?.setValidators([Validators.required]);
            feedbackControl?.updateValueAndValidity();
        } else {
            feedbackControl?.clearValidators();
            feedbackControl?.updateValueAndValidity();
        }

        if (!this.formularioValido) return;

        const { analise, quantidadeDeferida, feedback } = this.formulario.value;

        try {
            const payload: any = {
                beneficiario: this.data.beneficiario,
                obs: analise,
                fluxoEspecifico: fluxoEspecifico || null,
            };
    
            if (!fluxoEspecifico) {
                payload.quantidadeDeferida = quantidadeDeferida;
                payload.feedback = feedback;
            }
    
            const response = await apiBenecificarioAnaliseQuantidadeDiarias(payload);
            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            console.error(e)
            const detalheErro = e?.response?.data?.message || 'Não foi possível realizar a operação.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }
}
