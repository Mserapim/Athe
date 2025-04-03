import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigValorEditar } from 'api/diarias/config/api-diarias-config-valor-editar.service';
import { apiDiariasConfigValor } from 'api/diarias/config/api-diarias-config-valor.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import moment from 'moment';

class DiariasConfigValorEditarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'config-valor-editar',
    templateUrl: 'config-valor-editar.component.html',
    standalone: false
})
export class DiariasConfigValorEditarComponent extends MpmtFormularioComponent<DiariasConfigValorEditarComponentData> {

    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        valor_estado: new FormControl<number>(0, [Validators.required]),
        valor_fora_estado: new FormControl<number>(0, [Validators.required]),
        valor_exterior: new FormControl<number>(0, [Validators.required]),
        dt_inicio_vigencia: new FormControl<string | null>(null, [Validators.required]),
        dt_fim_vigencia: new FormControl<string | null>(null, []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigValorEditarComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigValorEditarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id, valor_estado, valor_fora_estado, valor_exterior, dt_inicio_vigencia, dt_fim_vigencia } =
                await apiDiariasConfigValor({
                    id: this.data.id,
                });

            await this.formulario.patchValue({
                id,
                valor_estado, 
                valor_fora_estado, 
                valor_exterior, 
                dt_inicio_vigencia, 
                dt_fim_vigencia,
            });
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        this.formulario.controls.dt_inicio_vigencia.setValue(moment(this.formulario.controls.dt_inicio_vigencia.value).format('YYYY-MM-DD'))
        if (this.formulario.controls.dt_fim_vigencia.value) {
            this.formulario.controls.dt_fim_vigencia.setValue(moment(this.formulario.controls.dt_fim_vigencia.value).format('YYYY-MM-DD'))
        }

        const { id, valor_estado, valor_fora_estado, valor_exterior, dt_inicio_vigencia, dt_fim_vigencia } = this.formulario.value;

        try {
            const {} = await apiDiariasConfigValorEditar({
                id,
                valor_estado, 
                valor_fora_estado, 
                valor_exterior, 
                dt_inicio_vigencia, 
                dt_fim_vigencia,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao editar o valor. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }
}
