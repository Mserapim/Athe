import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBenecificarioAnaliseValorDeferido } from 'api/diarias/aprovacoes-beneficiario/analise-valor-deferido-diarias.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class EditarValorDeferidoDiariasData {
    beneficiarioID: number;
    extrato: any;
    onClose?: Function;
}

@Component({
    selector: 'valor-liquido-deferido-editar',
    templateUrl: 'valor-liquido-deferido-editar.component.html',
    standalone: false
})
export class EditarValorDeferidoDiariasComponent extends MpmtFormularioComponent<EditarValorDeferidoDiariasData> implements OnInit{
    extrato = this.data.extrato;

    protected formulario = new FormGroup({
        valorDeferido: new FormControl<string>(null, [Validators.required]),
    });

    
    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: EditarValorDeferidoDiariasData,
        protected dialogRef: MatDialogRef<EditarValorDeferidoDiariasData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    async irAlterarValor() {
        if (!this.formularioValido) return;

        const { valorDeferido } = this.formulario.value;
        const valorNumerico = parseFloat(valorDeferido.replace('R$', '').replace(/\s/g, '').replace(',', '.'));
        
        try {
            const payload: any = {
                beneficiarioID: this.data.beneficiarioID,
                valorDeferido: valorNumerico,
            };
    
            const response = await apiBenecificarioAnaliseValorDeferido(payload);
            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            console.error(e)
            const detalheErro = e?.response?.data?.message || 'Não foi possível realizar sa operação.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }

    formatarMoeda(event: string) {
        let value = event.replace(/\D/g, '');
    
        if (value) {
            value = (parseFloat(value) / 100).toFixed(2);
            this.formulario.patchValue({ valorDeferido: `R$ ${value.replace('.', ',')}` });
        }
    }
}
