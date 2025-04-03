import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBenecificarioInformacaoEAprovacao } from 'api/diarias/aprovacoes-beneficiario/informacao-e-aprovacao.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariaAssessoriaAfatsamentoPGJData {
    beneficiario: number;
    titulo: string;
    onClose?: Function;
}

@Component({
    selector: 'assessoria-pgj-afastamento',
    templateUrl: 'assessoria-pgj-afastamento.component.html',
    standalone: false
})
export class DiariaAssessoriaAfatsamentoPGJComponent extends MpmtFormularioComponent<DiariaAssessoriaAfatsamentoPGJData> implements OnInit{
    public clickedAnalisar: boolean = false;
    
    protected formulario = new FormGroup({
        informacao: new FormControl<string>('', [Validators.required]),
        feedback: new FormControl<string>(null, [Validators.required]),
    });

    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariaAssessoriaAfatsamentoPGJData,
        protected dialogRef: MatDialogRef<DiariaAssessoriaAfatsamentoPGJData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    async irDeferir(deferir: boolean) {
        this.clickedAnalisar = true;
        if (!this.formularioValido) return;

        const { informacao, feedback } = this.formulario.value;

        try {
            const response = await apiBenecificarioInformacaoEAprovacao({
                beneficiario: this.data.beneficiario,
                acaoDeferimento: deferir,
                obs: informacao,
                feedback: feedback,
            });
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
