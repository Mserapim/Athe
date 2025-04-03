import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { DateRange } from '@angular/material/datepicker';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasEventoCriar } from 'api/diarias/api-diarias-evento-criar.service';
import { apiDiariasEventoEditar } from 'api/diarias/api-diarias-evento-editar.service';
import { apiDiariasEvento } from 'api/diarias/api-diarias-evento.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { formatDate } from 'utils/format-date';

class FormularioEventoComponentData {
    beneficiario: number;
    evento?: number;
    onClose?: Function;
}

@Component({
    selector: 'formulario-evento',
    templateUrl: 'formulario-evento.component.html',
    standalone: false
})
export class FormularioEventoComponent extends MpmtFormularioComponent<FormularioEventoComponentData> {
    singleDateSelected: boolean = true;

    protected formulario = new FormGroup({
        titulo: new FormControl<string>(''),
        singleDate: new FormControl(true),
        data: new FormControl<Date | null>(null),
        dateRange: new FormGroup({
            data_inicio: new FormControl<Date | null>(null),
            data_fim: new FormControl<Date | null>(null),
        }),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: FormularioEventoComponentData,
        protected dialogRef: MatDialogRef<FormularioEventoComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    ngOnInit() {
        this.carregarDados();

        this.formulario.get('singleDate')?.valueChanges.subscribe((value) => {
            this.singleDateSelected = value;
            if (value) {
                this.formulario.get('dateRange')?.disable();
                this.formulario.get('data')?.enable();
            } else {
                this.formulario.get('dateRange')?.enable();
                this.formulario.get('data')?.disable();
            }
        });
    }

    async carregarDados() {
        if (this.data.evento != null) {
            const results = await apiDiariasEvento({ id: this.data.evento });

            // Setando o valor do título e da data de início
            this.formulario.get('titulo')?.setValue(results.titulo);
            this.formulario.get('data')?.setValue(results.data_inicio);
            // Setando o valor de data_inicio e data_fim
            this.formulario.get('dateRange')?.patchValue({
                data_inicio: results.data_inicio,
                data_fim: results.data_fim,
            });

            // Verificando se data_fim é null para definir singleDateSelected
            if (results.data_fim == null) {
                this.singleDateSelected = true;
                this.formulario.get('singleDate')?.setValue(true);
                this.formulario.get('dateRange')?.disable();
                this.formulario.get('data')?.enable();
            } else {
                this.singleDateSelected = false;
                this.formulario.get('singleDate')?.setValue(false);
                this.formulario.get('dateRange')?.enable();
                this.formulario.get('data')?.disable();
            }
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { titulo, data, dateRange, singleDate } = this.formulario.value;
        let dt_inicio: Date | string | null = null;
        let dt_fim: Date | string | null = null;

        if (singleDate) {
            dt_inicio = data;
            dt_fim = null;

            if (typeof dt_inicio != 'string') {
                dt_inicio = formatDate(dt_inicio);
            }
        } else {
            dt_inicio = dateRange?.data_inicio;
            dt_fim = dateRange?.data_fim;

            if (typeof dt_inicio != 'string') {
                dt_inicio = formatDate(dt_inicio);
            }

            if (typeof dt_fim != 'string') {
                dt_fim = formatDate(dt_fim);
            }
        }

        try {
            let result;
            if (this.data.evento == null) {
                result = await apiDiariasEventoCriar({
                    beneficiario: this.data.beneficiario,
                    titulo: titulo,
                    data_inicio: dt_inicio,
                    data_fim: dt_fim,
                });
            } else {
                result = await apiDiariasEventoEditar({
                    id: this.data.evento,
                    beneficiario: this.data.beneficiario,
                    titulo: titulo,
                    data_inicio: dt_inicio,
                    data_fim: dt_fim,
                });
            }

            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.error(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao processar o evento. ${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }
}
