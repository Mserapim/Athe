import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasBeneficiario } from 'api/diarias/api-diarias-beneficiario.service';
import { apiDiariasDestinos } from 'api/diarias/api-diarias-destinos.service';
import { apiDiariasViagem } from 'api/diarias/api-diarias-viagem.service';
import { apiDiariasContaDevolucao } from 'api/diarias/prestacao-contas/api-diarias-conta-devolucao.service';
import { apiDiariasPrestacaoContasAssinar } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas-assinar.service';
import { apiDiariasPrestacaoContasDeferir } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas-deferir.service';
import { apiDiariasPrestacaoContasEditar } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas-editar.service';
import { apiDiariasPrestacaoContasIndeferir } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas-indeferir.service';
import { apiDiariasPrestacaoContas } from 'api/diarias/prestacao-contas/api-diarias-prestacao-contas.service';
import { MpmtAssinadorComponent } from 'apps/core/mpmt-assinador/mpmt-assinador.component';
import { Documento } from 'components/mpmt-file-update/mpmt-file-update.component';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';



class PrestacaoContasComponentData {
    prestacao_contas_id?: number;
    avaliar?: boolean = false;
    visualizacao?: boolean = false;
    onClose?: Function;
}

@Component({
    selector: 'modal-prestacao-contas',
    templateUrl: './modal-prestacao-contas.component.html',
    styleUrls: ['./modal-prestacao-contas.component.scss'],
    standalone: false
})
export class PrestacaoContasComponent extends MpmtFormularioComponent<PrestacaoContasComponentData> {

    viagem: any = null;
    beneficiario: any = null;
    prestacao_contas: any = null;

    destinos: any[] = []

    anexos: any[] = []
    anexos_carregados: Documento[] = []

    loading = true; // Variável de controle para o estado de carregamento


    contaDevolucao: any = null;

    protected formulario = new FormGroup({

        viagem_realizada: new FormControl<boolean>(null, []),
        viagem_total: new FormControl<boolean>(null, []),

        valor_devolvido: new FormControl<number>(null, []),
        obs_servicos_executados: new FormControl<string>(null, []),
        obs_resultado: new FormControl<string>(null, []),
        obs: new FormControl<string>(null, []),
        obs_anlaise: new FormControl<string>(null, []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PrestacaoContasComponentData,
        protected dialogRef: MatDialogRef<PrestacaoContasComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
    ) {
        super(data, snackBar, dialogRef);
    }

    ngAfterViewInit() {
        this.loading = false;
    }

    ngOnInit() {
        this.carregarContaDevolucao();
        this.carregarDados();

        // this.formulario.get('viagem_realizada')?.valueChanges.subscribe(value => {
        //     const viagemTotalControl = this.formulario.get('viagem_total');
        //     if (value) {
        //         viagemTotalControl?.setValidators([Validators.required]);
        //     } else {
        //         viagemTotalControl?.clearValidators();
        //     }
        //     viagemTotalControl?.updateValueAndValidity();
        // });
    }

    async carregarDados() {

        if (this.data.prestacao_contas_id != null) {
            this.prestacao_contas = await apiDiariasPrestacaoContas({
                id: this.data.prestacao_contas_id
            });

            this.formulario.get('viagem_realizada').setValue(this.prestacao_contas.viagem_realizada);
            this.formulario.get('viagem_total').setValue(this.prestacao_contas.viagem_total);

            this.formulario.get('obs_servicos_executados').setValue(this.prestacao_contas.obs_servicos_executados);
            this.formulario.get('obs_resultado').setValue(this.prestacao_contas.obs_resultado);
            this.formulario.get('obs').setValue(this.prestacao_contas.obs);
            this.formulario.get('obs_anlaise').setValue(this.prestacao_contas.obs_anlaise);


            this.anexos_carregados = this.prestacao_contas.anexos.map((anexo: any) => {
                return {
                    id: anexo.id,
                    description: anexo.filename,
                    name: anexo.filename,
                    attachment_id: anexo.id,
                    originalName: anexo.filename
                };
            });



        }

        if (this.prestacao_contas.beneficiario != null) {
            this.beneficiario = await apiDiariasBeneficiario({
                id: this.prestacao_contas.beneficiario
            });
        }

        if (this.beneficiario != null) {
            const { results } = await apiDiariasDestinos({
                beneficiario: this.beneficiario.id
            });
            this.destinos = results
        }

        if (this.beneficiario.viagem != null) {
            this.viagem = await apiDiariasViagem({
                id: this.beneficiario.viagem
            });
        }
    }


    protected async confirmarFormulario() {
        this.salvarRascunho()
        this.fecharFormulario();
        this.data?.onClose();
    }


    protected async salvarRascunho() {
        if (!this.formularioValido) return;

        const { viagem_realizada, viagem_total, obs, obs_anlaise, obs_resultado, obs_servicos_executados } = this.formulario.value;
        const anexos = this.anexos

        try {
            const result = await apiDiariasPrestacaoContasEditar
                ({
                    id: this.prestacao_contas.id,
                    beneficiario: this.prestacao_contas.beneficiario,
                    viagem_realizada: viagem_realizada,
                    viagem_total: viagem_total,
                    obs: obs,
                    obs_anlaise: obs_anlaise,
                    obs_resultado: obs_resultado,
                    obs_servicos_executados: obs_servicos_executados,
                    anexos: anexos
                });
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao preencher a Prestação de contas. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }

    }

    protected async assinarPrestacao() {
        if (!this.formularioValido) return;

        this.salvarRascunho()

        this.dialog.open(MpmtAssinadorComponent, {
            data: {
                titulo: 'Assinar e Enviar a Prestação de contas ',
                onClose: async () => {
                    try {
                        const result = await apiDiariasPrestacaoContasAssinar
                            ({
                                id: this.prestacao_contas.id
                            });

                        this.fecharFormulario();
                        this.data?.onClose();

                    } catch (e: any) {
                        console.log(e);
                        const detalheErro = e?.response?.data?.message || '';
                        const texto = `Ocorreu um erro inesperado ao preencher a Prestação de contas. ${detalheErro}`;
                        this.exibirMensagem(
                            'Atenção',
                            texto
                        );
                    }
                },
            },
            panelClass: 'dialog-panel-gray-100',
        });

    }

    protected async deferirPrestacao() {
        if (!this.formularioValido) return;

        this.salvarRascunho()

        this.dialog.open(MpmtAssinadorComponent, {
            data: {
                titulo: 'Assinar e Enviar a Prestação de contas ',
                onClose: async () => {
                    try {
                        const result = await apiDiariasPrestacaoContasDeferir
                            ({
                                id: this.prestacao_contas.id
                            });

                        this.fecharFormulario();
                        this.data?.onClose();

                    } catch (e: any) {
                        console.log(e);
                        const detalheErro = e?.response?.data?.message || '';
                        const texto = `Ocorreu um erro inesperado ao preencher a Prestação de contas. ${detalheErro}`;
                        this.exibirMensagem(
                            'Atenção',
                            texto
                        );
                    }
                },
            },
            panelClass: 'dialog-panel-gray-100',
        });

    }

    protected async indeferirPrestacao() {
        if (!this.formularioValido) return;

        this.salvarRascunho()

        this.dialog.open(MpmtAssinadorComponent, {
            data: {
                titulo: 'Assinar e Enviar a Prestação de contas ',
                onClose: async () => {
                    try {
                        const result = await apiDiariasPrestacaoContasIndeferir
                            ({
                                id: this.prestacao_contas.id
                            });

                        this.fecharFormulario();
                        this.data?.onClose();

                    } catch (e: any) {
                        console.log(e);
                        const detalheErro = e?.response?.data?.message || '';
                        const texto = `Ocorreu um erro inesperado ao preencher a Prestação de contas. ${detalheErro}`;
                        this.exibirMensagem(
                            'Atenção',
                            texto
                        );
                    }
                },
            },
            panelClass: 'dialog-panel-gray-100',
        });

    }

    isViagemRealizada(): boolean {
        return this.formulario.get('viagem_realizada')?.value === true;
    }

    isViagemParcial(): boolean {
        return this.formulario.get('viagem_total')?.value === false;
    }

    protected async receberAnexos(dados: []) {
        this.anexos = dados
    }

    protected exibirObsAnalise():boolean{
        const obs_analise = this.formulario.get('obs_anlaise').value

        if(this.data.avaliar == true || this.data.visualizacao == true || (obs_analise != "" && obs_analise != null)){
            return true
        }
            return false
    }

    formatarBooleano = (valor: boolean) => valor ? 'Sim' : 'Não';


    async carregarContaDevolucao() {
        const result = await apiDiariasContaDevolucao({
        });
        this.contaDevolucao = result
    }

}