import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { PainelControleModuloNovoComponent } from '../painel-controle-modulo-novo/painel-controle-modulo-novo.component';
import { PainelControleModuloEditarComponent } from '../painel-controle-modulo-editar/painel-controle-modulo-editar.component';
import { PainelControleModulosService } from './painel-controle-modulos.service';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
@Component({
    selector: 'painel-controle-modulos',
    templateUrl: 'painel-controle-modulos.component.html',
    standalone: false
})
export class PainelControleModulosComponent implements OnInit {
    titulo = 'Módulos';

    constructor(
        public service: PainelControleModulosService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'ordem',
                titulo: 'Ordem',
                visivel: true,
            },
            {
                codigo: 'nome',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'sigla',
                titulo: 'Sigla',
                visivel: true,
            },
            {
                codigo: 'situacao',
                titulo: 'Situação',
                visivel: true,
            },
            {
                codigo: 'created_by',
                titulo: 'Criado por',
                visivel: false,
            },
            {
                codigo: 'modified_by',
                titulo: 'Modificado por',
                visivel: false,
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
                        aoClicar: (linha: any) => this.irEditarModulo(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoModulo() {
        this.dialog.open(PainelControleModuloNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarModulo(linha: { id: number }) {
        this.dialog.open(PainelControleModuloEditarComponent, {
            data: {
                pk: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    displayFn(row: any): string {
        const situacaoSelecionada = this.situacoes.find((x) => x.valor === row);

        if (situacaoSelecionada?.nome) return `${situacaoSelecionada?.nome}`;
        else return '';
    }

    situacoes = [
        { valor: null, nome: 'Todos' },
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];

    selecaoMenus: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: async (payload) => {
            return {
                results: this.situacoes.filter((x) => {
                    if (!payload.palavra_chave) return true;
                    return (
                        x.nome
                            ?.toUpperCase()
                            .indexOf(payload.palavra_chave?.toUpperCase()) != -1
                    );
                }),
            };
        },
        obterValor: (x) => x.valor,
    };
}
