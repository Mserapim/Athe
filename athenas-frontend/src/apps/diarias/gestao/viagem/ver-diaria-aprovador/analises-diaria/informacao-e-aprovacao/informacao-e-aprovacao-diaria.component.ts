import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBenecificarioInformacaoEAprovacao } from 'api/diarias/aprovacoes-beneficiario/informacao-e-aprovacao.service';
import { apiObservacaoHistoricoFluxoBeneficiario } from 'api/diarias/detalhe/api-historico-observacao-beneficiario.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariaInformacaoAprovadorData {
    beneficiario: number;
    titulo: string;
    reanalise: boolean;
    onClose?: Function;
}

@Component({
    selector: 'informacao-e-aprovacao-diaria',
    templateUrl: 'informacao-e-aprovacao-diaria.component.html',
    standalone: false
})
export class DiariaInformacaoAprovadorComponent extends MpmtFormularioComponent<DiariaInformacaoAprovadorData> implements OnInit{
    public clickedAnalisar: boolean = false;
    analise: any = {}
    
    protected formulario = new FormGroup({
        informacao: new FormControl<string>(''),
    });

    ngOnInit() {
        super.ngOnInit();

        if (this.analiseAfastamento(this.data.titulo)) {
            this.formulario.get('informacao')?.setValidators([Validators.required]);
        }
        
        this.buscarObservacao();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariaInformacaoAprovadorData,
        protected dialogRef: MatDialogRef<DiariaInformacaoAprovadorData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    async buscarObservacao() {
        try {
          const payload = { beneficiario: this.data.beneficiario };
          const analise = await apiObservacaoHistoricoFluxoBeneficiario(payload);
          
          if (analise) {
            this.analise = analise;
          }
        } catch (error) {
          console.error('Erro ao buscar a análise:', error);
        }
    }

    async irDeferir(deferir: boolean) {
        this.clickedAnalisar = true;
        if (!this.formularioValido) return;

        const { informacao } = this.formulario.value;

        try {
            const response = await apiBenecificarioInformacaoEAprovacao({
                beneficiario: this.data.beneficiario,
                acaoDeferimento: deferir,
                obs: informacao
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

    analiseAfastamento(titulo: string) {
        if (titulo === "Análise afastamentos - Assessoria da PGJ") {
            return true
        } else {
            return false
        }
    }
}
