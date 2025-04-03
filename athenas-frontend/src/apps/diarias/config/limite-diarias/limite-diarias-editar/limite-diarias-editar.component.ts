import { Component, Inject } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ValidatorFn, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasChoicesMotivosViagem } from 'api/diarias/choices/api-diarias-motivos-viagem.service';
import { apiLimiteDiarias } from 'api/diarias/config/limite-diarias/api-limite-diarias';
import { apiLimiteDiariasEditar } from 'api/diarias/config/limite-diarias/api-limite-diarias-editar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import moment from 'moment';

class LimiteDiariasEditarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'limite-diarias-editar',
    templateUrl: 'limite-diarias-editar.component.html',
    standalone: false
})
export class LimiteDiariasEditarComponent extends MpmtFormularioComponent<LimiteDiariasEditarComponentData> {
    motivos_viagem: any[] = [];

    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        tipo: new FormControl<string>('', [Validators.required]),
        referencia: new FormControl<string>('', [Validators.required]),
        motivos_viagem: new FormControl<number[]>([], [Validators.required]),
        limite: new FormControl<number>(null, [Validators.required]),
        ilimitado: new FormControl<boolean>(false),
        dt_inicio_vigencia: new FormControl<string | null>(null, [Validators.required]),
    }, { validators: this.limiteDiasValidator() });


    ngOnInit() {
        super.ngOnInit();
        this.carregarMotivosViagem();
        this.formulario.get('ilimitado').valueChanges.subscribe((ilimitado) => {
            if (ilimitado) {
                this.formulario.get('limite').disable();
                this.formulario.get('limite').setValue(null);
            } else {
                this.formulario.get('limite').enable();
            }
        });
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: LimiteDiariasEditarComponentData,
        protected dialogRef: MatDialogRef<LimiteDiariasEditarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id, tipo, referencia, motivos_viagem, limite, dt_inicio_vigencia } =
                await apiLimiteDiarias({
                    id: this.data.id,
                });

            this.formulario.patchValue({
                id,
                tipo, 
                referencia, 
                motivos_viagem, 
                limite, 
                ilimitado: limite === null,
                dt_inicio_vigencia
            });
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário.'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        this.formulario.controls.dt_inicio_vigencia.setValue(moment(this.formulario.controls.dt_inicio_vigencia.value).format('YYYY-MM-DD'))

        const { id, tipo, referencia, motivos_viagem, limite, dt_inicio_vigencia } = this.formulario.value;

        try {
            const {} = await apiLimiteDiariasEditar({
                id,
                tipo, 
                referencia, 
                motivos_viagem, 
                limite: this.formulario.get('ilimitado').value ? null : limite,
                dt_inicio_vigencia
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o limite. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    async carregarMotivosViagem() {
        try {
            this.motivos_viagem = (await apiDiariasChoicesMotivosViagem({})).results;
        } catch (error) {
            console.error('Erro ao carregar os motivos de Viagem:', error);
            this.exibirMensagem('Erro', 'Não foi possível carregar os motivos da viagem');
        }
    }

    limiteDiasValidator(): ValidatorFn {
        return (control: AbstractControl): { [key: string]: any } | null => {
            const referenciaControl = control.get('referencia');
            const limiteControl = control.get('limite');
    
            if (!referenciaControl || !limiteControl) {
                return null;
            }
    
            const referencia = referenciaControl.value;
            const limite = limiteControl.value;
    
            if (referencia === 'mensal' && limite > 30) {
                return { 'limiteMensalInvalido': true };
            } else if (referencia === 'anual' && limite > 365) {
                return { 'limiteAnualInvalido': true };
            }
    
            return null;
        };
    }

    get maxLimite() {
        return this.formulario.controls.referencia.value === 'mensal' ? 30 : 365;
    }

    tipos = [
        { id: 'membro', descricao: 'Membro' },
        { id: 'servidor', descricao: 'Servidor' },
    ];

    referencias = [
        { id: 'anual', descricao: 'Anual' },
        { id: 'mensal', descricao: 'Mensal' },
    ];
}
