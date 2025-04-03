import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiAnotacoesPessoaisDetalhes } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-detalhes.service';
import { apiAnotacoesPessoaisEditar } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-editar.service';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiAnotacaoPessoalTiposAnotacao } from 'api/anotacoes-pessoais/api-anotacoes-pessoal-minhas-anotacoes.service';
import { apiRhPublicacoes } from 'api/rh/api-rh-publicacoes.service';
import {
    Bold,
    ClassicEditor,
    Essentials,
    Italic,
    Mention,
    Paragraph,
    Undo,
} from 'ckeditor5';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';

import moment from 'moment';
import { ModalPublicacoesComponent } from '../publicacoes/modal-publicacoes/modal-publicacoes.component';

class AnotacoesPessoaisEditarComponentData {
    anotacao_id: number;
    onClose?: Function;
}

@Component({
    selector: 'anotacoes-pessoais-editar',
    templateUrl: 'anotacoes-pessoais-editar.component.html',
    standalone: false
})
export class AnotacoesPessoaisEditarComponent extends MpmtFormularioComponent<AnotacoesPessoaisEditarComponentData> {
    @ViewChild('selecaoTipo') selecaoTipo: MpmtSelecaoFormComponent;
    @ViewChild('selecaoTipoDocumento') selecaoTipoDocumento: MpmtSelecaoFormComponent;
    @ViewChild('selecaoPublicacao') selecaoPublicacao: MpmtSelecaoFormComponent;

    private publicacaoCarregada: number = null;
    private tipoCarregado: number = null;
    private tipoDocumentoCarregado: number = null;

    protected formulario = new FormGroup({
        servidor: new FormControl<number>(null, [Validators.required]),
        texto: new FormControl<string>('', [Validators.required]),
        publicacao: new FormControl<number>(null, [Validators.required]),
        tipo: new FormControl<number>(null, [Validators.required]),
        documento_ano: new FormControl<number>(null, [Validators.required]),
        documento_numero: new FormControl<string>(''),
        documento_tipo: new FormControl<number>(null, [Validators.required]),
        documento_data: new FormControl<string | Date>(''),
        data_efeito_inicio: new FormControl<Date>(null),
        data_efeito_fim: new FormControl<Date>(null),
        gedoc_numero: new FormControl<string>(''),

        publicacao_display: new FormControl<string>('', [Validators.required]),
        servidor_matricula: new FormControl<string>(''),
        servidor_nome: new FormControl<string>(''),
        data_publicacao: new FormControl<string | Date>(null, []),
        data_expedicao_publicacao: new FormControl<string | Date>(null, []),

        textoAtualizado: new FormControl<string>(''),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AnotacoesPessoaisEditarComponentData,
        protected dialogRef: MatDialogRef<AnotacoesPessoaisEditarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        public dialog: MatDialog

    ) {
        super(data, snackBar, dialogRef);

        this.dateAdapter.setLocale('pt-BR');
    }

    title = 'angular';

    public Editor = ClassicEditor;
    public config = {
        toolbar: ['undo', 'redo', '|', 'bold', 'italic'],
        plugins: [Bold, Essentials, Italic, Mention, Paragraph, Undo],
    };

    ngAfterViewInit() {
        this.carregarDados();
    }

    async carregarDados() {
        if (this.data.anotacao_id != null) {
            try {
                const response = await apiAnotacoesPessoaisDetalhes({
                    id: this.data.anotacao_id,
                });

                this.publicacaoCarregada = response.publicacao
                this.tipoCarregado = response.tipo
                this.selecaoTipo.limparSelecao();

                this.tipoDocumentoCarregado = response.documento_tipo
                this.selecaoTipoDocumento.limparSelecao();

                await this.formulario.patchValue({
                    ...(response as any),
                    texto: response.texto,
                    data_publicacao: this.formatarData(response.data_publicacao) || 'Não informado',
                    data_expedicao_publicacao: this.formatarData(response.data_expedicao_publicacao) || 'Não informado'
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

    protected irNovoPublicacao() {
        this.dialog.open(ModalPublicacoesComponent, {
            data: {
                onClose: (publicacao) => {
                    this.publicacaoCarregada = publicacao.id;
                    
                    this.formulario.patchValue({
                        publicacao: publicacao.id,
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
            width: '60%',
            height: '90%',
        });
    }

    protected irEditarPublicacao() {
        this.dialog.open(ModalPublicacoesComponent, {
            data: {
                selecionada: this.formulario.value.publicacao,
                onClose: (publicacao) => {
                    this.publicacaoCarregada = publicacao.id;

                    this.formulario.patchValue({
                        publicacao: publicacao.id,
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

    protected get publicacaoSelecionada(): boolean {
        if (this.formulario?.value?.publicacao == null) {
            return true
        }
        return false
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;
        
        const {
            servidor,
            publicacao,
            documento_ano,
            documento_data,
            documento_numero,
            data_efeito_fim,
            data_efeito_inicio,
            gedoc_numero,
            textoAtualizado,
            texto,
        } = this.formulario.value;

        const tipo = this.selecaoTipo.form_control.value;
        const documento_tipo = this.selecaoTipoDocumento.form_control.value;

        function extractDateString(date: any) {
            if (!date) return undefined;
            if (typeof date == 'string') return date;
            return date?.toDate()?.toISOString()?.substring(0, 10);
        }
        try {
            const { } = await apiAnotacoesPessoaisEditar({
                id: this.data.anotacao_id,
                servidor: servidor,
                publicacao: publicacao,
                tipo: tipo,
                documento_tipo: documento_tipo,
                documento_ano: documento_ano,
                documento_data: extractDateString(documento_data),
                documento_numero: documento_numero,
                data_efeito_fim: extractDateString(data_efeito_fim),
                data_efeito_inicio: extractDateString(data_efeito_inicio),
                gedoc_numero: gedoc_numero,
                texto: texto,
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

    selecaoAnotacaoPessoalTiposAnotacao: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiAnotacaoPessoalTiposAnotacao,
        obterFiltros: (payload) => {
            return {
                ...payload,
                id: this.tipoCarregado
            };
        },
        obterValor: 'value',
        obterTitulo: 'label',
    };

    selecaoAnotacaoPessoalTiposDocumentos: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiAnotacoesPessoaisTiposDocumentos,
        obterFiltros: (payload) => {
            return {
                ...payload,
                id: this.tipoDocumentoCarregado
            };
        },
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

    selecaoPublicacoes: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiRhPublicacoes,
        obterFiltros: (payload) => {
            return {
                ...payload,
                per_page: 100,
                id: this.publicacaoCarregada
            };
        },
        obterValor: 'id',
        obterTitulo: 'cache_unicode',
    };

    formatarData(data) {
        return data ? moment(data).format('DD/MM/YYYY') : '';
    }
}
