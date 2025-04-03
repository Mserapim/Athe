import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBeneficiarioDaaPassagemCriar } from 'api/diarias/analise-beneficiario/api-analise-daa-passagem-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DaaCriarPassagemAereaData {
    destinoId: number;
    onClose?: Function;
}

@Component({
    selector: 'daa-passagem-aerea-criar',
    templateUrl: 'daa-passagem-aerea-criar.component.html',
    standalone: false
})
export class DaaCriarPassagemAereaComponent extends MpmtFormularioComponent<DaaCriarPassagemAereaData> implements OnInit {
    anexos: any[] = [];

    protected formulario = new FormGroup({
        empresa: new FormControl<string>('', [Validators.required]),
        aeroporto: new FormControl<string>('', [Validators.required]),
        numeroBilhete: new FormControl<number>(null, [Validators.required]),
        dataVoo: new FormControl<Date>(null, [Validators.required]),
        horaSaidaVoo: new FormControl<string>(null, [Validators.required]),
    });

    ngOnInit() {
        super.ngOnInit();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DaaCriarPassagemAereaData,
        protected dialogRef: MatDialogRef<DaaCriarPassagemAereaData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { empresa, aeroporto, numeroBilhete, dataVoo, horaSaidaVoo } = this.formulario.value;
        const anexos = this.anexos;
        const dataFormatada = new Date(dataVoo);
        const horaFormatada = horaSaidaVoo.split(':');

        dataFormatada.setHours(parseInt(horaFormatada[0]), parseInt(horaFormatada[1]));
    
        const utcDatetime = new Date(dataFormatada.getTime() - dataFormatada.getTimezoneOffset() * 60000);

        try {
            const response = await apiBeneficiarioDaaPassagemCriar({
                destino: this.data.destinoId,
                empresa,
                aeroporto,
                numeroBilhete,
                dataHoraVoo: utcDatetime,
                anexos,
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

    protected async receberAnexos(dados: []) {
        this.anexos = dados;
    }

    get formularioValido(): boolean {
        return this.formulario.valid && this.anexos.length > 0;
    }
}
