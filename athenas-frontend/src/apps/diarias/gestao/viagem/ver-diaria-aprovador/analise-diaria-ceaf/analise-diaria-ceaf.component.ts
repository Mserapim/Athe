import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBeneficiarioAnaliseCeafCriar } from 'api/diarias/analise-beneficiario/api-analise-ceaf-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariaAnaliseCeafData {
    beneficiario: number;
    viagem: number;
    onClose?: Function;
}

@Component({
    selector: 'analise-diaria-ceaf',
    templateUrl: 'analise-diaria-ceaf.component.html',
    standalone: false
})
export class DiariaAnaliseCeafComponent extends MpmtFormularioComponent<DiariaAnaliseCeafData> implements OnInit{
    anexos: any[] = []

    protected formulario = new FormGroup({
        analise: new FormControl<string>('', [Validators.required]),
    });

    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariaAnaliseCeafData,
        protected dialogRef: MatDialogRef<DiariaAnaliseCeafData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { analise } = this.formulario.value;
        const anexos = this.anexos

        try {
            const {} = await apiBeneficiarioAnaliseCeafCriar({
                viagem: this.data.viagem,
                beneficiario: this.data.beneficiario,
                obs: analise,
                anexos
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o grupo. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    protected async receberAnexos(dados: []) {
        this.anexos = dados
    }
}
