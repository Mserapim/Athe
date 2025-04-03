import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBenecificarioAnaliseDefinExcedentes } from 'api/diarias/aprovacoes-beneficiario/analise-defin-excedente.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class AnaliseDefinExcedenteData {
    beneficiario: number;
    titulo: string;
    qtdTotalDiarias: number;
    onClose?: Function;
}

@Component({
    selector: 'analise-defin-excedente',
    templateUrl: 'analise-defin-excedente.component.html',
    standalone: false
})
export class AnaliseDefinExcedenteComponent extends MpmtFormularioComponent<AnaliseDefinExcedenteData> implements OnInit{
    anexos: any[] = []
    envioFormulario: boolean = false;
    anexoObrigatorio: boolean = false;

    protected formulario = new FormGroup({
        quantidadeTotal: new FormControl<number>(this.data.qtdTotalDiarias),
        quantidadeDeferida: new FormControl<number>(this.data.qtdTotalDiarias, []),
        gedoc: new FormControl<string>('', [Validators.required]),
    });

    
    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AnaliseDefinExcedenteData,
        protected dialogRef: MatDialogRef<AnaliseDefinExcedenteData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async receberAnexos(dados: []) {
        this.anexos = dados
    }

    async irAnalisar(acao: boolean) {
        this.envioFormulario = true;

        if (acao) {
            this.anexoObrigatorio = true;
            this.formulario.controls['quantidadeDeferida'].setValidators([Validators.required]);
        } else {
            this.anexoObrigatorio = false;
            this.formulario.controls['quantidadeDeferida'].clearValidators();
        }
        this.formulario.controls['quantidadeDeferida'].updateValueAndValidity();

        if (this.formulario.get('gedoc')?.invalid) {
            this.exibirMensagem('Atenção', 'O campo GEDOC é obrigatório.');
            return; 
        }

        if (!this.formularioValido) return;

        const { gedoc, quantidadeDeferida } = this.formulario.value;
        const anexos = this.anexos

        try {
            const payload: any = {
                beneficiario: this.data.beneficiario,
                gedoc,
                acaoDeferimento: acao,
                anexos
            };

            if (acao) {
                payload.quantidadeDeferida = quantidadeDeferida;
            }
    
            const response = await apiBenecificarioAnaliseDefinExcedentes(payload);
            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            console.error(e)
            const detalheErro = e?.response?.data?.message || 'Não foi possível realizar a operação.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    protected get formularioValido() {
        return this.formulario.get('gedoc')?.valid && (!this.formulario.get('quantidadeDeferida')?.hasError('required') || this.formulario.get('quantidadeDeferida')?.valid) && (!this.envioFormulario || this.anexos.length > 0);
    }

    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }
}
