import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoGruposMenus } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos-menus.service';
import { apiPainelControleControleAcessoMenuConfigCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-config-criar.service';
import { apiPainelControleControleAcessoMenuConfigs } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-configs.service';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';

export class PainelControleNavegacaoMenuEditarUsuariosComponentData {
    onClose?: Function;
    menuId?: number;
}

@Component({
    selector: 'painel-controle-navegacao-menu-editar-usuarios',
    templateUrl: 'painel-controle-navegacao-menu-editar-usuarios.component.html',
    standalone: false
})
export class PainelControleNavegacaoMenuEditarUsuariosComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('', []),
    });

    constructor(
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleNavegacaoMenuEditarUsuariosComponentData
    ) {
        super();
    }

    protected obterTitulo() {
        return 'Lista de usuario do grupo menu';
    }

    protected async obterColunas() {
        return {
            nome: 'Nome',
        };
    }

    protected async obterDados(filtros: any) {
        return {
            results: [
                {
                    nome: 'Usuário Fake 1',
                },
                {
                    nome: 'Usuário Fake 2',
                },
                {
                    nome: 'Usuário Fake 3',
                },
                {
                    nome: 'Usuário Fake 4',
                },
            ],
        };
        return await apiPainelControleControleAcessoModulos(filtros);
    }

    protected async obterFiltros() {
        return {
            ...this.filtros.value,
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
        };
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
