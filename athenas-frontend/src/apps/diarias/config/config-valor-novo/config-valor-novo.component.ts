import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigValorCriar } from 'api/diarias/config/api-diarias-config-valor-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import moment from 'moment';

class DiariasConfigValorNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'config-valor-novo',
    templateUrl: 'config-valor-novo.component.html',
    standalone: false
})
export class DiariasConfigValorNovoComponent extends MpmtFormularioComponent<DiariasConfigValorNovoComponentData> {
    protected formulario = new FormGroup({
        valor_estado: new FormControl<number>(0, [Validators.required]),
        valor_fora_estado: new FormControl<number>(0, [Validators.required]),
        valor_exterior: new FormControl<number>(0, [Validators.required]),
        dt_inicio_vigencia: new FormControl<string | null>(null, [Validators.required]),
        dt_fim_vigencia: new FormControl<string | null>(null, []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigValorNovoComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigValorNovoComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;
        
        this.formulario.controls.dt_inicio_vigencia.setValue(moment(this.formulario.controls.dt_inicio_vigencia.value).format('YYYY-MM-DD'))
        if (this.formulario.controls.dt_fim_vigencia.value) {
            this.formulario.controls.dt_fim_vigencia.setValue(moment(this.formulario.controls.dt_fim_vigencia.value).format('YYYY-MM-DD'))
        }

        const { valor_estado, valor_fora_estado, valor_exterior, dt_inicio_vigencia, dt_fim_vigencia } = this.formulario.value;

        try {
            const {} = await apiDiariasConfigValorCriar({
                valor_estado,
                valor_fora_estado,
                valor_exterior,
                dt_inicio_vigencia,
                dt_fim_vigencia
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o valor. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }
}
