import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { apiPainelControleControleAcessUsuarioAtualizarMastiff } from 'api/painel-controle/api-painel-controle-controle-acesso-usuario-atualizar-mastiff.service';
import { PainelControleUsuarioEditarComponent } from '../painel-controle-usuario-editar/painel-controle-usuario-editar.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiRhCategoriaFuncional } from 'api/rh/api-rh-categoria-funcional.service';
import { apiRhLotacao } from 'api/rh/api-rh-lotacao.service';
import {
    PainelControleUsuarioAtualizarGruposComponent,
    PainelControleUsuarioAtualizarGruposComponentData,
} from '../painel-controle-usuario-atualizar-grupos/painel-controle-usuario-atualizar-grupos.component';
import {
    PainelControleUsuarioEstruturaMenusComponent,
    PainelControleUsuarioEstrututaMenusComponentData,
} from '../painel-controle-usuario-atualizar-estrutura-menus/painel-controle-usuario-estrutura-menus.component';
import { PainelControleUsuariosService } from './painel-controle-usuarios.service';

@Component({
    selector: 'painel-controle-usuarios',
    templateUrl: 'painel-controle-usuarios.component.html',
    standalone: false
})
export class PainelControleUsuariosComponent implements OnInit {
    constructor(
        public service: PainelControleUsuariosService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'status',
                titulo: 'Ativo',
                tipo: 'BOLEANO_ICONE',
                visivel: true,
            },
            {
                codigo: 'username',
                titulo: 'Login',
                visivel: true,
            },
            {
                codigo: 'matricula',
                titulo: 'Matricula',
                visivel: true,
            },
            {
                codigo: 'nome',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'categoria_funcional',
                titulo: 'Categoria Funcional',
                visivel: true,
            },
            {
                codigo: 'lotacao',
                titulo: 'Lotação',
                visivel: true,
            },
            {
                codigo: 'qtd_grupos',
                titulo: 'Grupos',
                tipo: 'VER_MAIS',
                visivel: true,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        aoClicar: (linha: any) => this.irAtualizarGrupo(linha),
                    },
                ],
            },
            {
                codigo: 'qtd_menus',
                titulo: 'Funcionalidades',
                tipo: 'VER_MAIS',
                visivel: true,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        aoClicar: (linha: any) => this.irVerPermissoes(linha),
                    },
                ],
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
                        aoClicar: (linha: any) => this.irEditarUsuario(linha),
                    },
                    {
                        icone: 'refresh',
                        titulo: 'Atualizar pelo Mastiff',
                        requerPermissao: 'editar',
                        aoClicar: (linha: any) => this.atualizarMastiff(linha),
                    },
                ],
            },
        ]);
    }

    protected irEditarUsuario(linha: { id: number }) {
        this.dialog.open(PainelControleUsuarioEditarComponent, {
            data: {
                pk: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected atualizarMastiff(linha: { id: number }) {
        try {
            apiPainelControleControleAcessUsuarioAtualizarMastiff({
                servidor_id: linha.id,
            });
            this.service.recarregarListagem();
        } catch (e: any) {
            console.log(e);
        }
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    situacoes = [
        { valor: 'Todos', nome: 'Todos' },
        { valor: 'Ativo', nome: 'Ativo' },
        { valor: 'Inativo', nome: 'Inativo' },
    ];

    selecaoCatFuncional: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhCategoriaFuncional,
        obterValor: 'cod',
    };

    selecaoLotacao: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhLotacao,
        obterTitulo: 'name',
    };

    verificarTipo(valor: any): boolean {
        switch (typeof valor) {
            case 'boolean':
                return true;
            default:
                return false;
        }
    }

    irAtualizarGrupo(usuario: { pk: number }) {
        this.dialog.open(PainelControleUsuarioAtualizarGruposComponent, {
            data: <PainelControleUsuarioAtualizarGruposComponentData>{
                onClose: () => this.service.recarregarListagem(),
                usuario: usuario,
            },
            width: '80%',
        });
    }

    irVerPermissoes(usuario: { pk: number }) {
        const dialogRef = this.dialog.open(
            PainelControleUsuarioEstruturaMenusComponent,
            {
                data: <PainelControleUsuarioEstrututaMenusComponentData>{
                    onClose: () => this.service.recarregarListagem(),
                    usuario: usuario,
                },
                width: '60%',
            }
        );
    }
}
