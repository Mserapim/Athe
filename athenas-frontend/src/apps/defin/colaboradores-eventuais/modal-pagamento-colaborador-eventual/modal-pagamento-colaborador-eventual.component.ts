import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiCoreChoicesFormulario } from 'api/core/api-core-choices-formulario.service';
import { apiDefinPagamentoColaboradorEventualCriar } from 'api/defin/pagamento-colaborador-eventual/api-defin-pagamento-criar.service';
import { apiDefinPagamentoColaboradorEventualEditar } from 'api/defin/pagamento-colaborador-eventual/api-defin-pagamento-editar.service';
import { apiDefinPagamentoColaboradorEventual } from 'api/defin/pagamento-colaborador-eventual/api-defin-pagamento.service';
import { apiRhCbosService } from 'api/rh/cbo/api-rh-cbos-service';
import { apiRhLotacoesService } from 'api/rh/lotacao/api-rh-lotacoes-service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponentConfiguracao, MpmtSelecaoFormComponent } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';


class PagamentoColaboradorEventualModalComponentData {
    id?: number;
    colaborador_id?: number;
    onClose?: Function;
}

@Component({
    selector: 'modal-pagamento-colaborador-eventual',
    templateUrl: './modal-pagamento-colaborador-eventual.component.html',
    styleUrls: ['./modal-pagamento-colaborador-eventual.component.scss'],
    standalone: false,
})
export class PagamentoColaboradorEventualModalComponent extends MpmtFormularioComponent<PagamentoColaboradorEventualModalComponentData> {

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


    protected formulario = new FormGroup({
        cbo: new FormControl<number>(null, [Validators.required]),
        lotacao: new FormControl<number>(null, [Validators.required]),
        natureza_atividade: new FormControl<number>(null, [Validators.required]),
        data_pagamento: new FormControl<Date>(null, [Validators.required]),
        valor_bruto: new FormControl<number>(null, [Validators.required]),
        contribuicao_parcial: new FormControl<number>(0, [Validators.required]),
        isento_inss: new FormControl<boolean>(false, [Validators.required]),
        contribuido: new FormControl<boolean>(false, [Validators.required]),

    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PagamentoColaboradorEventualModalComponentData,
        protected dialogRef: MatDialogRef<PagamentoColaboradorEventualModalComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');

    }



    ngOnInit() {
        this.loading = true;

        this.formulario.get('contribuido')?.valueChanges.subscribe((valor) => {
            if (valor) {
                this.formulario.get('contribuicao_parcial')?.setValidators([Validators.required]);

            } else {
                this.formulario.get('contribuicao_parcial')?.clearValidators();

            }
        });

    }

    ngAfterViewInit() {
        if (this.data.id == null) {
            this.loading = false;
        }
    }

    ngAfterViewChecked() {
        if (this.loading && this.data.id != null) {
            this.carregarDados();
            this.loading = false;
        }

    }

    async carregarDados() {
        if (this.data.id != null) {
            try {
                const response = await apiDefinPagamentoColaboradorEventual({
                    id: this.data.id,
                });

                await this.formulario.patchValue({
                    ...(response as any),

                });
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

            const {
                cbo,
                lotacao,
                natureza_atividade,
                data_pagamento,
                valor_bruto,
                contribuicao_parcial,
                isento_inss,
                contribuido,

            } = this.formulario.value;

            var data_formatada = null

            if (typeof data_pagamento == 'string') {
                data_formatada = data_pagamento
            } else {
                data_formatada = data_pagamento.toISOString().split('T')[0]
            }

            if (this.data.id == null) {

                const result = await apiDefinPagamentoColaboradorEventualCriar({
                    cbo: cbo,
                    lotacao: lotacao,
                    natureza_atividade: natureza_atividade,
                    data_pagamento: data_formatada,
                    valor_bruto: valor_bruto,
                    contribuicao_parcial: contribuicao_parcial,
                    isento_inss: isento_inss,
                    contribuido: contribuido,
                    pessoa: this.data.colaborador_id,
                });

            } else {
                const result = await apiDefinPagamentoColaboradorEventualEditar({
                    id: this.data?.id,
                    cbo: cbo,
                    lotacao: lotacao,
                    natureza_atividade: natureza_atividade,
                    data_pagamento: data_formatada,
                    valor_bruto: valor_bruto,
                    contribuicao_parcial: contribuicao_parcial,
                    isento_inss: isento_inss,
                    contribuido: contribuido,
                    pessoa: this.data.colaborador_id,
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



    selecaoCbo: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiRhCbosService,
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave };
        },
        obterValor: 'id',
        obterTitulo: 'unicode',
    };


    selecaoLotacao: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiRhLotacoesService,
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave };
        },
        obterValor: 'id',
        obterTitulo: 'nome',
    };


    selecaoNaturezaAtividade: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiCoreChoicesFormulario,
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, app: 'defin', name: 'NATURE_ACTIVITY', per_page: 100 };
        },
        obterValor: 'valor',
        obterTitulo: 'display',
    };

}