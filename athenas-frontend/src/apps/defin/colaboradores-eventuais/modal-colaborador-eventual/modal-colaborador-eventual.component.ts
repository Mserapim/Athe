import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiCoreChoicesFormulario } from 'api/core/api-core-choices-formulario.service';
import { apiDefinColaboradorEventualCriar } from 'api/defin/colaborador-eventual/api-defin-colaborador-eventual-criar.service';
import { apiDefinColaboradorEventualEditar } from 'api/defin/colaborador-eventual/api-defin-colaborador-eventual-editar.service';
import { apiDefinColaboradorEventual } from 'api/defin/colaborador-eventual/api-defin-colaborador-eventual.service';
import { apiDiariasConfigCargos } from 'api/diarias/config/api-diarias-config-cargos.service';
import { apiRhPaises } from 'api/rh/api-rh-paises';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponentConfiguracao, MpmtSelecaoFormComponent } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';


import { MAT_DATE_LOCALE } from '@angular/material/core';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';

class ColaboradorEventualModalComponentData {
    colaborador_id?: number;
    onClose?: Function;
}

@Component({
    selector: 'modal-colaborador-eventual',
    templateUrl: './modal-colaborador-eventual.component.html',
    styleUrls: ['./modal-colaborador-eventual.component.scss'],
    standalone: false,
    providers: [
        { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
        provideMomentDateAdapter(),
    ]
})
export class ColaboradorEventualModalComponent extends MpmtFormularioComponent<ColaboradorEventualModalComponentData> {

    @ViewChild('selecaoRacaCor') selecaoRacaCorComponente: MpmtSelecaoFormComponent;
    @ViewChild('selecaoCategoriaEsocial') selecaoCategoriaEsocialComponente: MpmtSelecaoFormComponent;
    @ViewChild('selecaoCargoEventual') selecaoCargoEventualComponente: MpmtSelecaoFormComponent;
    @ViewChild('selecaoPaisNaturalidade') selecaoPaisNaturalidadeComponente: MpmtSelecaoFormComponent;
    @ViewChild('selecaoPaisNacionalidade') selecaoPaisNacionalidadeComponente: MpmtSelecaoFormComponent;


    sexos: { valor: string; nome: string }[] = []; // Inicializar como array vazio

    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    loading = true; // Variável de controle para o estado de carregamento

    selecaoRacaCor: MpmtSelecaoFormComponentConfiguracao = null;
    selecaoCategoriaEsocial: MpmtSelecaoFormComponentConfiguracao = null;
    selecaoCargoEventual: MpmtSelecaoFormComponentConfiguracao = null;
    selecaoPaisNacionalidade: MpmtSelecaoFormComponentConfiguracao = null;
    selecaoPaisNaturalidade: MpmtSelecaoFormComponentConfiguracao = null;


    private cargoEventualCarregado: number = null;
    private naturalidadeCarregado: number = null;
    private nacionalidadeCarregado: number = null;


    protected formulario = new FormGroup({
        nome_social: new FormControl<string>('', [Validators.required]),
        cpf: new FormControl<string>('', [Validators.required]),
        email: new FormControl<string>('', [Validators.required]),
        data_nascimento: new FormControl<Date>(null, [Validators.required]),
        sexo: new FormControl<string>('N', [Validators.required]),
        raca_cor: new FormControl<number>(null, [Validators.required]),
        pais_naturalidade: new FormControl<number>(null, [Validators.required]),
        pais_nacionalidade: new FormControl<number>(null, [Validators.required]),
        categoria_esocial: new FormControl<number>(null, [Validators.required]),
        cargo_eventual: new FormControl<number>(null, [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ColaboradorEventualModalComponentData,
        protected dialogRef: MatDialogRef<ColaboradorEventualModalComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');

    }



    ngOnInit() {
        this.loading = true;

        this.sexos = [
            { valor: 'M', nome: 'MASCULINO' },
            { valor: 'F', nome: 'FEMININO' },
            { valor: 'N', nome: 'NÃO INFORMADO' },
        ];

        this.carregarSelecoesConf();
    }

    ngAfterViewInit() {
        if (this.data.colaborador_id == null) {
            this.loading = false;
        }
    }

    ngAfterViewChecked() {
        if (this.loading && this.data.colaborador_id != null) {
            this.carregarDados();
            this.loading = false;
        }

    }

    async carregarDados() {
        if (this.data.colaborador_id != null) {
            try {
                const response = await apiDefinColaboradorEventual({
                    id: this.data.colaborador_id,
                });

                await this.formulario.patchValue({
                    ...(response as any),

                });


                this.cargoEventualCarregado = response.cargo_eventual
                this.naturalidadeCarregado = response.pais_naturalidade
                this.nacionalidadeCarregado = response.pais_naturalidade

                this.selecaoPaisNacionalidadeComponente?.limparSelecao();
                this.selecaoPaisNaturalidadeComponente?.limparSelecao();
                this.selecaoCargoEventualComponente?.limparSelecao();
                // this.selecaoRacaCorComponente?.limparSelecao();
                // this.selecaoCategoriaEsocialComponente?.limparSelecao();
            } catch (e) {
                console.error(e);
                this.exibirMensagem(
                    'Atenção',
                    'Erro inesperado ao carregar os valores do formulário'
                );
            }

        }
    }


    protected async confirmarFormulario() {
        try {

            const { nome_social,
                cpf,
                email,
                data_nascimento,
                sexo,
                raca_cor,
                pais_naturalidade,
                pais_nacionalidade,
                categoria_esocial,
                cargo_eventual
            } = this.formulario.value;

            var data_formatada = null
            
            if (typeof data_nascimento == 'string') {
                data_formatada = data_nascimento
            } else {
                data_formatada = data_nascimento.toISOString().split('T')[0]
            }

            if (this.data.colaborador_id == null) {

                const result = await apiDefinColaboradorEventualCriar({
                    nome_social: nome_social,
                    cpf: cpf,
                    email: email,
                    data_nascimento: data_formatada,
                    sexo: sexo,
                    raca_cor: raca_cor,
                    pais_naturalidade: pais_naturalidade,
                    pais_nacionalidade: pais_nacionalidade,
                    cargo_eventual: cargo_eventual,
                    categoria_esocial: categoria_esocial
                });

            } else {
                const result = await apiDefinColaboradorEventualEditar({
                    id: this.data.colaborador_id,
                    nome_social: nome_social,
                    cpf: cpf,
                    email: email,
                    data_nascimento: data_formatada,
                    sexo: sexo,
                    raca_cor: raca_cor,
                    pais_naturalidade: pais_naturalidade,
                    pais_nacionalidade: pais_nacionalidade,
                    cargo_eventual: cargo_eventual,
                    categoria_esocial: categoria_esocial
                });

            }
            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            console.error(e);
            const detalheErro = e?.response?.data?.message || e?.message || '';
            const texto = `${detalheErro}`;
            this.exibirMensagem('Aviso', texto);
        }
    }


    private carregarSelecoesConf() {
        this.selecaoRacaCor = {
            obterOpcoes: apiCoreChoicesFormulario,
            obterFiltros: payload => {
                return { palavra_chave: payload.palavra_chave, app: 'rh', name: 'TYPE_RACE' };
            },
            obterValor: 'valor',
            obterTitulo: 'display',
        };

        this.selecaoCategoriaEsocial = {
            obterOpcoes: apiCoreChoicesFormulario,
            obterFiltros: payload => {
                return { palavra_chave: payload.palavra_chave, app: 'rh', name: 'CATEGORY_WORKER' };
            },
            obterValor: 'valor',
            obterTitulo: 'display',
        };


        this.selecaoCargoEventual = {
            obterOpcoes: apiDiariasConfigCargos,
            obterFiltros: payload => {
                return {
                    palavra_chave: payload.palavra_chave,
                    per_page: 100,
                    id: this.cargoEventualCarregado
                };
            },
            obterValor: 'id',
            obterTitulo: 'nome',
        };

        this.selecaoPaisNacionalidade = {
            obterOpcoes: apiRhPaises,
            obterFiltros: payload => {
                return {
                    palavra_chave: payload.palavra_chave,
                    per_page: 100,
                    id: this.naturalidadeCarregado
                };
            },
            obterValor: 'id',
            obterTitulo: 'nome',
        };

        this.selecaoPaisNaturalidade = {
            obterOpcoes: apiRhPaises,
            obterFiltros: payload => {
                return {
                    palavra_chave: payload.palavra_chave,
                    per_page: 100,
                    id: this.nacionalidadeCarregado
                };
            },
            obterValor: 'id',
            obterTitulo: 'nome',
        };

    }

    displayFn(valor: string): string {
        const sexo = this.sexos?.find(s => s.valor === valor);
        return sexo ? sexo.nome : '';
    }


}