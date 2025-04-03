import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { AnotacoesPessoaisListagemService } from './anotacoes-pessoais-listagem.service';
import { apiPainelControleControleAcessoUsuarios } from 'api/painel-controle/api-painel-controle-controle-acesso-usuarios.service';
import { AnotacoesPessoaisNovoComponent } from '../anotacoes-pessoais-novo/anotacoes-pessoais-novo.component';
import { AnotacoesPessoaisEditarComponent } from '../anotacoes-pessoais-editar/anotacoes-pessoais-editar.component';
import { AnotacoesPessoaisVisualizarComponent } from '../anotacoes-pessoais-visualizar/anotacoes-pessoais-visualizar.component';
import { apiReportAnotacaoPessoalAnotacoesPessoaisService } from 'api/report/api-report-anotacao-pessoal-anotacoes-pessoais]';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { apiAnotacoesPessoaisOcultar } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-ocultar.service';

import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiAnotacaoPessoalTiposAnotacao } from 'api/anotacoes-pessoais/api-anotacoes-pessoal-minhas-anotacoes.service';


@Component({
    selector: 'anotacoes-pessoais-listagem',
    templateUrl: 'anotacoes-pessoais-listagem.component.html',
    standalone: false
})
export class AnotacoesPessoaisListagemComponent implements OnInit {
    apiAnotacoesPessoaisTiposDocumentos = apiAnotacoesPessoaisTiposDocumentos;
    apiAnotacaoPessoalTiposAnotacao = apiAnotacaoPessoalTiposAnotacao;

    constructor(
        public service: AnotacoesPessoaisListagemService,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        public navegacaoAtualService: NavegacaoAtualService,
        private _fuseConfirmationService: FuseConfirmationService

    ) {
    }

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
        this.service.carregarTiposAntotacao();
        this.service.carregarTiposDocumento();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'servidor_nome',
                titulo: 'Nome do servidor',
                visivel: true,
            },
            {
                codigo: 'tipo_display',
                titulo: 'Tipo da anotação',
                visivel: true,
            },
            {
                codigo: 'documento_tipo_display',
                titulo: 'Tipo do documento',
                visivel: true,
            },
            {
                codigo: 'publicacao_display',
                titulo: 'Publicação',
                visivel: true,
            },
            {
                codigo: 'data_publicacao',
                titulo: 'Data da publicação',
                visivel: true,
                tipo: 'DATA',
            },
            {
                codigo: 'documento_numero',
                titulo: 'Número do documento',
                visivel: true,
            },
            {
                codigo: 'documento_ano',
                titulo: 'Ano do documento',
                visivel: true,
            },
            {
                codigo: 'documento_data',
                titulo: 'Data do documento',
                visivel: true,
                tipo: 'DATA',
            },
            {
                codigo: 'data_efeito_inicio',
                titulo: 'Data de efeito início',
                visivel: true,
                tipo: 'DATA',
            },
            {
                codigo: 'data_efeito_fim',
                titulo: 'Data de efeito fim',
                visivel: true,
                tipo: 'DATA',
            },
            {
                codigo: 'gedoc_numero',
                titulo: 'Número do GEDOC',
                visivel: true,
            },
            {
                codigo: 'created_by',
                titulo: 'Criado por',
                visivel: false,
            },
            {
                codigo: 'created_at',
                titulo: 'Criado em',
                visivel: false,
                tipo: 'DATA_HORA',
            },
            {
                codigo: 'modified_by',
                titulo: 'Modificado por',
                visivel: false,
            },
            {
                codigo: 'modified_at',
                titulo: 'Modificado em',
                visivel: false,
                tipo: 'DATA_HORA',

            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'heroicons_outline:eye',
                        titulo: 'Visualizar',
                        requerPermissao: 'ler',
                        aoClicar: (linha: any) => this.irVisualizar(linha),
                    },
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        requerPermissao: 'editar',
                        aoClicar: (linha: any) => this.irEditar(linha),
                    },
                    {
                        icone: 'cancel',
                        titulo: 'Ocultar',
                        requerPermissao: 'apagar',
                        aoClicar: (linha: any) => this.irOcultar(linha),
                    },
                ],
            },
        ]);
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    protected irNovo() {
        this.dialog.open(AnotacoesPessoaisNovoComponent, {
            data: {
                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
            height: '90%',
        });
    }
    
    protected irEditar(linha: any) {
        this.dialog.open(AnotacoesPessoaisEditarComponent, {
            data: {
                onClose: () => this.service.recarregarListagem(),
                anotacao_id: linha.id,
            },
            width: '80%',
            height: '90%',
        });
    }
    protected irOcultar(linha: any) {

        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja ocultar a anotação?',
            icon: {
            show: true,
            name: 'heroicons_outline:exclamation',
            color: 'warn'
            },
            actions: {
                confirm: {
                show: true,
                label: 'Ocultar',
                style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                show: true,
                label: 'Cancelar',
                style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });
    
        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                try {
                    
                    result = await apiAnotacoesPessoaisOcultar({
                        id: linha.id
                    });
                    
                    this.exibirMensagem('', "Anotação oculta com sucesso.")

                    this.service.recarregarListagem();
        
        
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });
    }

    protected irVisualizar(linha: any) {
        this.dialog.open(AnotacoesPessoaisVisualizarComponent, {
            data: {
                onClose: () => this.service.recarregarListagem(),
                anotacao_id: linha.id,
            },
            width: '80%',
            height: '90%',
        });
    }

    situacoes = [
        { valor: 'Todos', nome: 'Todos' },
        { valor: 'Ativo', nome: 'Ativo' },
        { valor: 'Inativo', nome: 'Inativo' },
    ];

    selecaoServidores: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiPainelControleControleAcessoUsuarios,
        obterValor: 'id',
        obterTitulo: async (payload: any) =>
            `${payload.matricula} - ${payload.nome}`,
        obterFiltros: (payload) => {
            return {
                ...payload,
                per_page: 10,
            };
        },
    };

    verificarTipo(valor: any): boolean {
        switch (typeof valor) {
            case 'boolean':
                return true;
            default:
                return false;
        }
    }

    protected async irGerarRelatorio() {
        const { servidor_ids, tipos_anotacao, tipos_documento } =
            this.service.filtros.value;
            var servidor_id = null;
            if( servidor_ids.length > 0){
                this.exibirErro('Para gerar o relatório selecione apenas um Servidor');
                return false;
            }else{
                servidor_id = servidor_ids[0].pk;
            }


        try {
            const result =
                await apiReportAnotacaoPessoalAnotacoesPessoaisService({
                    servidor: servidor_id,
                    tipos_anotacao: tipos_anotacao,
                    tipos_documento: tipos_documento ,
                    notificar: true,
                });

            this.exibirMensagem('', result.message, 'sucess-snackbar');
        } catch (e: any) {
            console.error(e);
            this.exibirErro(e);
        }
    }

    protected get servidorSelecionado() {
        return this.service.filtros.get('servidor_ids').value != null;
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected exibirErro(e: any) {
        const detalheErro = e?.response?.data?.message || '';
        const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }
}
