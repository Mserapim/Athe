import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiAnotacaoPessoalTiposAnotacao } from 'api/anotacoes-pessoais/api-anotacoes-pessoal-minhas-anotacoes.service';
import { apiAnotacoesPessoaisTiposDocumentos } from 'api/anotacoes-pessoais/api-anotacoes-pessoais-tipos-documentos.service';
import { apiPainelControleControleAcessoUsuarios } from 'api/painel-controle/api-painel-controle-controle-acesso-usuarios.service';
import { AnotacoesPessoaisNovoComponent } from '../anotacoes-pessoais-novo/anotacoes-pessoais-novo.component';
import { AnotacoesPessoaisPublicacoesService } from './anotacoes-pessoais-publicacoes.service';
import { AnotacoesPessoaisPublicacaoNovoComponent } from '../anotacoes-pessoais-publicacao-novo/anotacoes-pessoais-publicacao-novo.component';
import { AnotacoesPessoaisPublicacaoEditarComponent } from '../anotacoes-pessoais-publicacao-editar/anotacoes-pessoais-publicacao-editar.component';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';

@Component({
    selector: 'anotacoes-pessoais-publicacoes',
    templateUrl: 'anotacoes-pessoais-publicacoes.component.html',
    standalone: false
})
export class AnotacoesPessoaisPublicacoesComponent implements OnInit {
    constructor(
        public service: AnotacoesPessoaisPublicacoesService,
        public dialog: MatDialog,
        public navegacaoAtualService: NavegacaoAtualService
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
        this.service.carregarTiposPublicacao();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: true,
            },
            {
                codigo: 'cache_unicode',
                titulo: 'Título',
                visivel: true,
            },
            {
                codigo: 'tipo_display',
                titulo: 'Tipo de publicação',
                visivel: true,
            },
            {
                codigo: 'document',
                titulo: 'Documento',
                visivel: true,
            },
            {
                codigo: 'veiculo_publicacao_display',
                titulo: 'Veículo de publicação',
                visivel: true,
            },
            {
                codigo: 'data_vigencia',
                titulo: 'Data de vigência',
                visivel: true,
                tipo: 'DATA',

            },
            {
                codigo: 'data_publicacao',
                titulo: 'Data de publicação',
                visivel: true,
                tipo: 'DATA',

            },
            {
                codigo: 'import_siap',
                titulo: 'Importado do SIAP',
                visivel: false,
                tipo: 'BOLEANO_ICONE',
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
                        icone: 'edit',
                        titulo: 'Editar',
                        requerPermissao: 'editar',
                        aoClicar: (linha: any) => this.irEditar(linha),
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
        this.dialog.open(AnotacoesPessoaisPublicacaoNovoComponent, {
            data: {
                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
            height: '90%',
        });
    }

    protected irEditar(linha: any) {
        this.dialog.open(AnotacoesPessoaisPublicacaoEditarComponent, {
            data: {
                onClose: () => this.service.recarregarListagem(),
                id: linha.id,
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
}
