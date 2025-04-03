import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiRhOrgaoGeral } from 'api/rh/api-rh-orgao-geral.service';
import { apiRhPublicacaoEditar } from 'api/rh/api-rh-publicacao-editar.service';
import { apiRhPublicacao } from 'api/rh/api-rh-publicacao.service';
import { apiRhVeiculoPublicacao } from 'api/rh/api-rh-veiculo-publicacao.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';

class AnotacoesPessoaisEditarComponentData {
    onClose?: Function;
    id: string;
}

@Component({
    selector: 'anotacoes-pessoais-publicacao-editar',
    templateUrl: 'anotacoes-pessoais-publicacao-editar.component.html',
    standalone: false
})
export class AnotacoesPessoaisPublicacaoEditarComponent
    extends MpmtFormularioComponent<AnotacoesPessoaisEditarComponentData>
    implements OnInit
{

    @ViewChild('selecaoTipo') selecaoTipo: MpmtSelecaoFormComponent;
    @ViewChild('selecaoOrigem') selecaoOrigem: MpmtSelecaoFormComponent;
    @ViewChild('selecaoVeiculoPublicacao') selecaoVeiculoPublicacao: MpmtSelecaoFormComponent;

    tipos: any[] = [];
    origens: any[] = [];
    veiculos: any[] = [];
    
    selectedTipo: string;

    protected formulario = new FormGroup({
        id: new FormControl<string>('', []),
        numero: new FormControl<string>('', []),
        tipo: new FormControl<number>(null),
        origem: new FormControl<number>(null, []),
        data_expedicao: new FormControl<string>(null, [Validators.required]),
        data_vigencia: new FormControl<string>(null, [Validators.required]),
        veiculo_publicacao: new FormControl<number>(null, []),
        numero_publicacao: new FormControl<string>(null, []),
        data_publicacao: new FormControl<Date>(null, []),
        vehicle_page: new FormControl<number>(null, []),
        interessado_nome: new FormControl<string>(null, []),
        arquivo: new FormControl<{ valor: string; titulo: string }>(null, []),
        interno: new FormControl<boolean>(false, []),
        observacao: new FormControl<string>(null, []),
        document: new FormControl<string>(null, []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AnotacoesPessoaisEditarComponentData,
        protected dialogRef: MatDialogRef<AnotacoesPessoaisEditarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>
    ) {
        super(data, snackBar, dialogRef);

        this.dateAdapter.setLocale('pt-BR');
    }

    ngOnInit() {
        super.ngOnInit();
        this.carregarTipos();
        this.carregarOrigens();
        this.carregarVeiculos();
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        if (!this.data.id) return;

        try {
            const response = await apiRhPublicacao({
                id: this.data.id,
            });

            const publicacao = response;

            await this.formulario.patchValue({
                ...(response as any),
                arquivo: {
                    valor: publicacao.arquivo,
                    titulo: publicacao.arquivo_display,
                },
                tipo: publicacao.tipo,
                origem: publicacao.origem,
                veiculo_publicacao: publicacao.veiculo_publicacao,
            });
        } catch (e) {
            console.error(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const data = this.formulario.value;

        const tipo = this.selecaoTipo.form_control.value;
        const origem = this.selecaoOrigem.form_control.value;
        const veiculo_publicacao = this.selecaoVeiculoPublicacao.form_control.value;

        function extractDateString(date: any) {
            if (!date) return undefined;
            if (typeof date == 'string') return date;
            return date?.toDate()?.toISOString()?.substring(0, 10);
        }
        try {
            const response: any = await apiRhPublicacaoEditar({
                ...(data as any),
                data_vigencia: extractDateString(data.data_vigencia),
                data_expedicao: extractDateString(data.data_expedicao),
                data_publicacao: extractDateString(data.data_publicacao),
                tipo: tipo,
                origem: origem,
                veiculo_publicacao: veiculo_publicacao,
                arquivo: data.arquivo?.valor,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose(response.data);
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }

    async carregarTipos() {
        try {
            const response = await this.selecoesAnotacaoPessoalTiposDocumentos.obterOpcoes({});
            if (response && response.results) {
                this.tipos = response.results.map(item => ({
                    label: item.label,
                    value: item.value,
                }));
            }
        } catch (error) {
            console.error('Erro ao carregar os tipos:', error);
        }
    }

    async carregarOrigens() {
        try {
            const response = await this.selecoesOrgaoGeral.obterOpcoes({});
            if (response && response.results) {
                this.origens = response.results.map(item => ({
                    label: item.nome,
                    value: item.id,
                }));
            }
        } catch (error) {
            console.error('Erro ao carregar as origens:', error);
        }
    }

    async carregarVeiculos() {
        try {
            const response = await this.selecoesVeiculoPublicacao.obterOpcoes({});
            if (response && response.results) {
                this.veiculos = response.results.map(item => ({
                    label: item.label,
                    value: item.value,
                }));
            }
        } catch (error) {
            console.error('Erro ao carregar os veículos:', error);
        }
    }

    selecoesOrgaoGeral: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiRhOrgaoGeral,
        obterValor: 'id',
        obterTitulo: 'nome',
    };

    selecoesVeiculoPublicacao: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiRhVeiculoPublicacao,
        obterValor: 'value',
        obterTitulo: 'label',
    };

    selecoesAnotacaoPessoalTiposDocumentos = {
        obterOpcoes: apiAnotacoesPessoaisTiposDocumentos,
        obterValor: 'value',
        obterTitulo: 'label',
    };

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];
}
