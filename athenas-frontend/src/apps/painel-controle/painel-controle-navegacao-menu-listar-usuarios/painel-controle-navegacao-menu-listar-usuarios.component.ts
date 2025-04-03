import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { apiPainelControleControleAcessoMenuMenusConfigsUsuarios } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-menus-configs-usuarios';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';


export class PainelControleNavegacaoMenuListarUsuariosComponentData {
    onClose?: Function;
    menuId?: number;
}

@Component({
    selector: 'painel-controle-navegacao-menu-listar-usuarios',
    templateUrl: 'painel-controle-navegacao-menu-listar-usuarios.component.html',
    standalone: false
})
export class PainelControleNavegacaoMenuListarUsuariosComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    constructor(
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleNavegacaoMenuListarUsuariosComponentData
    ) {
        super();
    }

    protected obterTitulo() {
        return 'Lista de usuários do grupo de menu';
    }

    protected async obterColunas() {
        return {
            matricula: 'Matrícula',
            nome: 'Nome',
            grupos: 'Grupos de acesso',
        };
    }

    protected async obterDados() {
        const filtros = await this.obterFiltros();
        try {
            const data = await apiPainelControleControleAcessoMenuMenusConfigsUsuarios(filtros);
            const results = data.results.map(user => ({
                ...user,
                grupos: this.formatarGrupos(user.grupos)
            }));
            return {
                results: results,
                total: data.total,
            };
        } catch (error) {
            console.error('Erro ao obter dados:', error);
            return { results: [] };
        }
    }

    formatarGrupos(grupos: string[]): string {
        return grupos.join(', ');
    }

    protected async obterFiltros() {
        return {
            palavra_chave: this.filtros.get('palavra_chave')?.value || '',
            menu_id: this.data.menuId,
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
        };
    }

    displayFn(row: any): string {
        return row ? `${row.nome}` : '';
    }
}