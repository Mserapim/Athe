import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { apiRhSevidorService } from 'api/rh/api-rh-servidor.service';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiRhDadosBancariosBancos } from 'api/rh/api-rh-dados-bancarios-bancos.service';
import { apiRhDadosBancariosServidorContaCriar } from 'api/rh/api-rh-dados-bancarios-servidor-conta-criar.service';

class NovaContaComponentData {
    servidor_id: number;
    onClose?: Function;
}

@Component({
    selector: 'nova-conta',
    templateUrl: 'nova-conta.component.html',
    standalone: false
})
export class NovaContaComponent extends MpmtFormularioComponent<NovaContaComponentData> {
    
    servidor: any = null


    protected formulario = new FormGroup({
        banco: new FormControl<number>(null, [Validators.required]),
        tipo_conta: new FormControl<number>(1, [Validators.required]),
        agencia_numero: new FormControl<string>(null, [Validators.required, this.validarNumeros]),
        agencia_dv: new FormControl<string>(null, []),
        conta_numero: new FormControl<string>(null, [Validators.required, this.validarNumeros]),
        conta_dv: new FormControl<string>(null, [Validators.required]),
        
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: NovaContaComponentData,
        protected dialogRef: MatDialogRef<NovaContaComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        this.carregarDadosServidor();
    }


    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { banco, tipo_conta, agencia_numero, agencia_dv, conta_numero, conta_dv } = this.formulario.value;


        try {
            const result = await apiRhDadosBancariosServidorContaCriar({
                servidor: this.data.servidor_id,
                banco: banco,
                tipo_conta: tipo_conta,
                agencia_numero: agencia_numero,
                agencia_dv: agencia_dv,
                conta_numero: conta_numero,
                conta_dv: conta_dv,
            });

            this.fecharFormulario();

            this.dialogRef.close({
                conta: result.id,
               });
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao criar a conta. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
                
    }

    selecaoBancos: MpmtSelecaoComponentConfiguracao = {
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave }; 
        },
        obterOpcoes: apiRhDadosBancariosBancos,
        obterTitulo: 'unicode',
    };

    public async carregarDadosServidor() {
        try {
            this.servidor = (await apiRhSevidorService({id:this.data.servidor_id}));
        } catch (error) {
            console.error('Erro ao carregar dados do servidor:', error);
        }
    }


    tipos_conta = [
        { id: 1, descricao: 'Conta Corrente' },
    ];

    validarNumeros(control: FormControl) {
        const valor = control.value;
        const somenteNumeros = /^[0-9]+$/;
        return somenteNumeros.test(valor) ? null : { somenteNumeros: true };
    }

}
