import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { apiRhDadosBancariosServidorContas } from 'api/rh/api-rh-dados-bancarios-servidor-contas.service';
import { apiRhSevidorService } from 'api/rh/api-rh-servidor.service';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiRhDadosBancariosBancos } from 'api/rh/api-rh-dados-bancarios-bancos.service';
import { apiRhDadosBancariosTiposConta } from 'api/rh/api-rh-dados-bancarios-tipos-conta.service';
import { apiRhDadosBancariosServidorContaCriar } from 'api/rh/api-rh-dados-bancarios-servidor-conta-criar.service';
import { apiDiariasConfigCargos } from 'api/diarias/config/api-diarias-config-cargos.service';
import { apiDiariasColaboradorEventualCriar } from 'api/diarias/api-diarias-novo-colaborador-eventual';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';

class NovoBeneficiarioExternoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'novo-colaborador-eventual',
    templateUrl: 'novo-colaborador-eventual.component.html',
    standalone: false
})
export class NovoColaboradorEventualComponent extends MpmtFormularioComponent<NovoBeneficiarioExternoComponentData> {
    
    servidor: any = null


    protected formulario = new FormGroup({
        nome: new FormControl<string>(null, [Validators.required]),
        email: new FormControl<string>(null, [Validators.required]),
        cpf: new FormControl<string>(null, [Validators.required]),
        data_nasc: new FormControl<Date>(null, [Validators.required]),
        cargo: new FormControl<number>(null, [Validators.required]),

        banco: new FormControl<number>(null, [Validators.required]),
        tipo_conta: new FormControl<number>(1, [Validators.required]),
        agencia_numero: new FormControl<string>(null, [Validators.required, this.validarNumeros]),
        agencia_dv: new FormControl<string>(null, []),
        conta_numero: new FormControl<string>(null, [Validators.required, this.validarNumeros]),
        conta_dv: new FormControl<string>(null, [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: NovoBeneficiarioExternoComponentData,
        protected dialogRef: MatDialogRef<NovoBeneficiarioExternoComponentData>,
        protected snackBar: MatSnackBar,
        protected stepper: DiariaStepperService,

    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
    }


    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, cpf, email, cargo, data_nasc, banco, tipo_conta, agencia_numero, agencia_dv, conta_numero, conta_dv } = this.formulario.value;


        try {
            const result = await apiDiariasColaboradorEventualCriar({
                viagem: this.stepper.id_viagem,
                nome: nome,
                cpf: cpf,
                email: email,
                cargo: cargo,
                data_nasc: data_nasc,
                banco: banco,
                tipo_conta: tipo_conta,
                agencia_numero: agencia_numero,
                agencia_dv: agencia_dv,
                conta_numero: conta_numero,
                conta_dv: conta_dv,
            });

            this.fecharFormulario();
            this.data?.onClose();

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
    

    selecaoCargos: MpmtSelecaoComponentConfiguracao = {
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave }; 
        },
        obterOpcoes: apiDiariasConfigCargos,
        // obterTitulo: 'unicode',
    };
    
    selecaoBancos: MpmtSelecaoComponentConfiguracao = {
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave }; 
        },
        obterOpcoes: apiRhDadosBancariosBancos,
        obterTitulo: 'unicode',
    };


    tipos_conta = [
        { id: 1, descricao: 'Conta Corrente' },
    ];

    validarNumeros(control: FormControl) {
        const valor = control.value;
        const somenteNumeros = /^[0-9]+$/;
        return somenteNumeros.test(valor) ? null : { somenteNumeros: true };
    }
}
