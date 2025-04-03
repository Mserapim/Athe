import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiAnaliseDefinOrdemBancariaCriar } from 'api/diarias/analise-beneficiario/api-analise-defin-ordem-bancaria.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariaAnaliseDefinOrdemBancariaData {
    beneficiario: number;
    viagem: number;
    onClose?: Function;
}

@Component({
    selector: 'analise-diaria-defin-ordem-bancaria',
    templateUrl: 'analise-defin-ordem-bancaria.component.html',
    standalone: false
})
export class DiariaAnaliseDefinOrdemBancariaComponent extends MpmtFormularioComponent<DiariaAnaliseDefinOrdemBancariaData> implements OnInit{
    anexos: any[] = []

    protected formulario = new FormGroup({
        numeroOrdemBancaria: new FormControl<number>(null),
        dataPagamento: new FormControl<Date>(null),
    });

    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariaAnaliseDefinOrdemBancariaData,
        protected dialogRef: MatDialogRef<DiariaAnaliseDefinOrdemBancariaData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { numeroOrdemBancaria, dataPagamento } = this.formulario.value;
        const anexos = this.anexos

        try {
            const payload: any = {
                viagem: this.data.viagem,
                beneficiario: this.data.beneficiario,
                numero_ordem_bancaria: numeroOrdemBancaria,
                anexos,
            };
    
            if (dataPagamento) {
                const dataPagamentoDate = new Date(dataPagamento);
                payload.data_pagamento = dataPagamentoDate.toISOString().split('T')[0];
            }
    
            await apiAnaliseDefinOrdemBancariaCriar(payload);

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
