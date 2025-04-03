import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBenecificarioAnaliseQuantidadeDiarias } from 'api/diarias/aprovacoes-beneficiario/analise-quantidade-diarias.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class AnaliseAssessoriaDgDiariasData {
    beneficiario: number;
    titulo: string;
    excedente: boolean;
    possuiExcedente: boolean;
    qtdTotalDiarias: number;
    finalidadeAcompanhamento: boolean;
    ehServidor: boolean;
    onClose?: Function;
}

@Component({
    selector: 'analise-assessoria-dg',
    templateUrl: 'analise-assessoria-dg.component.html',
    standalone: false
})
export class AnaliseAssessoriaDgDiariasComponent extends MpmtFormularioComponent<AnaliseAssessoriaDgDiariasData> implements OnInit{
    public clickedAnalisar: boolean = false;

    protected formulario = new FormGroup({
        quantidadeTotal: new FormControl<number>(this.data.qtdTotalDiarias),
        quantidadeDeferida: new FormControl<number>(this.data.qtdTotalDiarias, [Validators.required]),
        analise: new FormControl<string>('', [Validators.required]),
        acompanhandoAutoridade: new FormControl<boolean>(null),
        feedback: new FormControl<string>(null, [Validators.required]),
    });

    
    ngOnInit() {
        super.ngOnInit();

        if (this.data.excedente || this.data.possuiExcedente) {
            this.formulario.controls['quantidadeDeferida'].disable();
        }

        if (this.data.finalidadeAcompanhamento && this.data.ehServidor) {
            this.formulario.controls['acompanhandoAutoridade'].setValidators([Validators.required]);
        }
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AnaliseAssessoriaDgDiariasData,
        protected dialogRef: MatDialogRef<AnaliseAssessoriaDgDiariasData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    async irAnalisar() {
        this.clickedAnalisar = true;
        if (!this.formularioValido) return;

        const { analise, quantidadeDeferida, acompanhandoAutoridade, feedback } = this.formulario.value;

        try {
            const payload: any = {
                beneficiario: this.data.beneficiario,
                obs: analise,
                quantidadeDeferida: quantidadeDeferida,
                acompanhandoAutoridade: acompanhandoAutoridade,
                feedback: feedback,
            };
    
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
