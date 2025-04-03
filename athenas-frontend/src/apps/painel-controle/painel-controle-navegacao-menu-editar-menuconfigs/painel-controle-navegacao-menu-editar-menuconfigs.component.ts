import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { PainelControleModuloNovoComponent } from '../painel-controle-modulo-novo/painel-controle-modulo-novo.component';
import { PainelControleModuloEditarComponent } from '../painel-controle-modulo-editar/painel-controle-modulo-editar.component';
import { apiPainelControleControleAcessoMenuConfigs } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-configs.service';
import { apiPainelControleControleAcessoMenuConfigApagar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-config-apagar.service ';
import {
    PainelControleGrupoAtualizarUsuariosComponent,
    PainelControleGrupoAtualizarUsuariosComponentData,
} from '../painel-controle-grupo-atualizar-usuarios/painel-controle-grupo-atualizar-usuarios.component';

@Component({
    selector: 'painel-controle-navegacao-menu-editar-menuconfigs',
    templateUrl: 'painel-controle-navegacao-menu-editar-menuconfigs.component.html',
    standalone: false
})
export class PainelControleNavegacaoMenuEditarMenuConfigsComponent extends MpmtListagemComponent {
    @Input() refreshKey?: number;
    @Input() menuId: number;

    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('', []),
    });

    constructor(public dialog: MatDialog) {
        super();
    }

    protected obterTitulo() {
        return 'Módulos';
    }

    ngOnChanges(changes: SimpleChanges): void {
        this.aplicarFiltros();
    }

    protected async obterColunas() {
        return {
            id: 'Código',
            usuario_grupo_nome: 'Nome do Grupo',
            acoes: 'Ações',
        };
    }

    protected async obterDados(filtros: any) {
        const response = await apiPainelControleControleAcessoMenuConfigs({
            ...filtros,
            menu_id: this.menuId,
        });

        return {
            ...response,
            results: response.results.map((x) => {
                return {
                    ...x,
                    acoes: (x?.acoes || []).join(', '),
                };
            }),
        };
    }

    protected async obterFiltros() {
        return {
            ...this.filtros.value,
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
        };
    }

    protected irNovoModulo() {
        this.dialog.open(PainelControleModuloNovoComponent, {
            data: { onClose: () => this.aplicarFiltros() },
        });
    }

    protected irEditarModulo(linha: { id: number }) {
        this.dialog.open(PainelControleModuloEditarComponent, {
            data: {
                pk: linha.id,
                onClose: () => this.aplicarFiltros(),
            },
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    async deleteItem(row: any) {
        try {
            await apiPainelControleControleAcessoMenuConfigApagar({
                id: row.id,
            });
            this.configurarDados();
        } catch (e) {
            console.error(e);
        }
    }

    protected irEditarGrupo(linha: { id: number }) {
        this.dialog.open(PainelControleGrupoAtualizarUsuariosComponent, {
            data: <PainelControleGrupoAtualizarUsuariosComponentData>{
                usuario_grupo: linha,
                onClose: () => this.aplicarFiltros(),
            },
            width: '80%',
        });
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];
}
