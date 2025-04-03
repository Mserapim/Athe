import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiAnotacoesPessoaisCriar } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-criar.service';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiAnotacaoPessoalTiposAnotacao } from 'api/anotacoes-pessoais/api-anotacoes-pessoal-minhas-anotacoes.service';
import { apiRhPublicacoes } from 'api/rh/api-rh-publicacoes.service';
import { apiRhSevidoresService } from 'api/rh/api-rh-servidores.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import {
    MpmtSelecaoComponent,
    MpmtSelecaoComponentConfiguracao,
} from 'components/mpmt-selecao/mpmt-selecao.component';
import moment from 'moment';
import { ModalPublicacoesComponent } from '../publicacoes/modal-publicacoes/modal-publicacoes.component';

class AnotacoesPessoaisNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'anotacoes-pessoais-novo',
    templateUrl: 'anotacoes-pessoais-novo.component.html',
    styles: [
        `
            :host ::ng-deep .ck-editor__editable_inline {
                min-height: 180px;
            }
        `,
    ],
    standalone: false
})
export class AnotacoesPessoaisNovoComponent extends MpmtFormularioComponent<AnotacoesPessoaisNovoComponentData> {
    @ViewChild('documentoTipoSelecao')
    documentoTipoSelecao: MpmtSelecaoComponent;

    apiRhSevidoresService = apiRhSevidoresService;


    protected formulario = new FormGroup({
        data_publicacao: new FormControl<string | Date>(null, []),
        data_expedicao_publicacao: new FormControl<string | Date>(null, []),
        documento_data: new FormControl<string>(''),
        documento_numero: new FormControl<string>('', [Validators.required]),
        servidor: new FormControl<any>(null, [Validators.required]),
        documento_ano: new FormControl<string | number>(null, [
            Validators.required,
        ]),
        documento_tipo: new FormControl<string | number | null>(null, [
            Validators.required,
        ]),
        tipo: new FormControl<number | null>(null, [Validators.required]),
        tipo_anotacao_id: new FormControl<number>(null),
        gedoc_numero: new FormControl<string>(''),
        matricula: new FormControl<string>(''),
        servidor_nome: new FormControl<string>(''),
        tipo_display: new FormControl<string>(''),
        publicacao: new FormControl<{
            valor: number;
            titulo: string;
        }>({ valor: null, titulo: null }),
        data_efeito_inicio: new FormControl<string>(''),
        data_efeito_fim: new FormControl<string>(''),
        documento_tipo_display: new FormControl<string>(''),
        texto: new FormControl<string>(''),
        textoAtualizado: new FormControl<string>('', [Validators.required]),
        publicacao_display: new FormControl<string>('', []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AnotacoesPessoaisNovoComponentData,
        protected dialogRef: MatDialogRef<AnotacoesPessoaisNovoComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        public dialog: MatDialog
    ) {
        super(data, snackBar, dialogRef);

        this.dateAdapter.setLocale('pt-BR');
    }

    protected irNovoPublicacao() {
        this.dialog.open(ModalPublicacoesComponent, {
            data: {
                onClose: (publicacao) => {
                    this.formulario.patchValue({
                        publicacao: {
                            valor: publicacao.id,
                            titulo: publicacao.unicode,
                        },
                        publicacao_display: publicacao.cache_unicode,
                        data_publicacao: this.formatarData(
                            publicacao.data_publicacao
                        ),
                        data_expedicao_publicacao: this.formatarData(
                            publicacao.data_expedicao
                        ),
                    });
                },
            },
            width: '80%',
            height: '90%',
        });
    }

    protected irEditarPublicacao() {
        this.dialog.open(ModalPublicacoesComponent, {
            data: {
                selecionada: this.formulario.value.publicacao?.valor,
                onClose: (publicacao) => {
                    this.formulario.patchValue({
                        publicacao: {
                            valor: publicacao.id,
                            titulo: publicacao.unicode,
                        },
                        publicacao_display: publicacao.cache_unicode,
                        data_publicacao: this.formatarData(
                            publicacao.data_publicacao
                        ),
                        data_expedicao_publicacao: this.formatarData(
                            publicacao.data_expedicao
                        ),
                    });
                },
            },
            width: '80%',
            height: '90%',
        });
    }

    protected async resetarFormulario() {
        super.resetarFormulario();
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const {
            texto,
            textoAtualizado,
            tipo,
            documento_numero,
            documento_ano,
            documento_tipo,
            documento_data,
            data_efeito_inicio,
            data_efeito_fim,
            gedoc_numero,
            servidor,
            publicacao,
        } = this.formulario.value;

        function extractDateString(date: any) {
            if (!date) return undefined;
            if (typeof date == 'string') return date;
            return date?.toDate()?.toISOString()?.substring(0, 10);
        }
        try {
            const {} = await apiAnotacoesPessoaisCriar({
                servidor:servidor?.pk,
                documento_ano,
                documento_data: extractDateString(documento_data),
                documento_numero,
                data_efeito_fim: extractDateString(data_efeito_fim),
                data_efeito_inicio: extractDateString(data_efeito_inicio),
                documento_tipo,
                gedoc_numero,
                texto: textoAtualizado,
                tipo,
                publicacao: publicacao?.valor,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }


    selecaoPublicacoes: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhPublicacoes,
        obterFiltros: (payload) => {
            return {
                ...payload,
                per_page: 10,
            };
        },
        obterValor: 'id',
        obterTitulo: 'unicode',
    };

    selecaoAnotacaoPessoalTiposAnotacao: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiAnotacaoPessoalTiposAnotacao,
        obterValor: 'value',
        obterTitulo: 'label',
    };

    selecaoAnotacaoPessoalTiposDocumentos: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiAnotacoesPessoaisTiposDocumentos,
        obterValor: 'value',
        obterTitulo: 'label',
    };

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];

    updateText($event) {
        const texto = $event?.editor?.getData();
        this.formulario.patchValue({
            textoAtualizado: texto,
        });
    }

    formatarData(data) {
        return data ? moment(data).format('DD/MM/YYYY') : '';
    }
}
