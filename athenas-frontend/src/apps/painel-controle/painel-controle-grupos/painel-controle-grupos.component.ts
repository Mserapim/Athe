import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { PainelControleModuloEditarComponent } from '../painel-controle-modulo-editar/painel-controle-modulo-editar.component';
import { apiPainelControleControleAcessoGrupos } from '../../../api/painel-controle/api-painel-controle-controle-acesso-grupos.service';
import { PainelControleGrupoNovoComponent } from '../painel-controle-grupo-novo/painel-controle-grupo-novo.component';
import { PainelControleGrupoEditarComponent } from '../painel-controle-grupo-editar/painel-controle-grupo-editar.component';
import {
    PainelControleGrupoMenuEditarComponent,
    PainelControleGrupoMenuEditarComponentData,
} from '../painel-controle-grupo-menu-editar/painel-controle-grupo-menu-editar.component';
import {
    PainelControleGrupoAtualizarUsuariosComponent,
    PainelControleGrupoAtualizarUsuariosComponentData,
} from '../painel-controle-grupo-atualizar-usuarios/painel-controle-grupo-atualizar-usuarios.component';
import { PainelControleGruposService } from './painel-controle-grupos.service';

@Component({
    selector: 'painel-controle-grupo-acesso',
    templateUrl: 'painel-controle-grupos.component.html',
    standalone: false
})
export class PainelControleGruposComponent implements OnInit {
    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('ATIVO', []),
    });

    constructor(
        public service: PainelControleGruposService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'nome',
                titulo: 'Nome',
                visivel: true,
            },
            {
                codigo: 'menus_qtd',
                titulo: 'Menus',
                visivel: true,
                tipo: 'VER_MAIS',
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        aoClicar: (linha: any) =>
                            this.irMenuConfigEditar(linha),
                    },
                ],
            },
            {
                codigo: 'usuarios_qtd',
                titulo: 'Usuários',
                visivel: true,
                tipo: 'VER_MAIS',
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        aoClicar: (linha: any) =>
                            this.irGrupoAtualizarUsuario(linha),
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
                        aoClicar: (linha: any) => this.irEditarGrupo(linha),
                    },
                ],
            },
        ]);
    }

    protected irNovoGrupo() {
        this.dialog.open(PainelControleGrupoNovoComponent, {
            data: { onClose: () => this.service.recarregarListagem() },
        });
    }

    protected irEditarGrupo(linha: { id: number }) {
        this.dialog.open(PainelControleGrupoEditarComponent, {
            data: {
                id: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected irMenuConfigEditar(linha: { id: number }) {
        this.dialog.open(PainelControleGrupoMenuEditarComponent, {
            data: <PainelControleGrupoMenuEditarComponentData>{
                usuarioGrupoId: linha.id,
                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
            height: '90%',
        }).afterClosed().subscribe(() => this.service.recarregarListagem());
    }

    protected irGrupoAtualizarUsuario(linha: { id: number }) {
        this.dialog.open(PainelControleGrupoAtualizarUsuariosComponent, {
            data: <PainelControleGrupoAtualizarUsuariosComponentData>{
                grupo: linha,
                onClose: () => this.service.recarregarListagem(),
            },
            width: '80%',
            height: '90%',
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];
}
