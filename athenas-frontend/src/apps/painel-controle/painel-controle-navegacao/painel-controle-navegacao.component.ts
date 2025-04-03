import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiPainelControleControleAcessoGruposMenus } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos-menus.service';
import { PainelControleNavegacaoGrupoMenuCriarComponent } from '../painel-controle-navegacao-grupo-menu-criar/painel-controle-navegacao-grupo-menu-criar.component';
import {
    PainelControleNavegacaoMenuCriarComponent,
    PainelControleNavegacaoMenuCriarComponentData,
} from '../painel-controle-navegacao-menu-criar/painel-controle-navegacao-menu-criar.component';
import {
    PainelControleNavegacaoMenuListarUsuariosComponent,
    PainelControleNavegacaoMenuListarUsuariosComponentData,
} from '../painel-controle-navegacao-menu-listar-usuarios/painel-controle-navegacao-menu-listar-usuarios.component';
import { PainelControleNavegacaoGrupoMenuEditarComponent } from '../painel-controle-navegacao-grupo-menu-editar/painel-controle-navegacao-grupo-menu-editar.component';
import {
    PainelControleNavegacaoMenuEditarConfiguracaoComponent,
    PainelControleNavegacaoMenuEditarConfiguracaoComponentData,
} from '../painel-controle-navegacao-menu-editar-configuracoes/painel-controle-navegacao-menu-editar.component';
import {
    PainelControleNavegacaoMenuEditarComponent,
    PainelControleNavegacaoMenuEditarComponentData,
} from '../painel-controle-navegacao-menu-editar/painel-controle-navegacao-menu-editar.component';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';

@Component({
    selector: 'painel-controle-navegacao',
    templateUrl: 'painel-controle-navegacao.component.html',
    standalone: false
})
export class PainelControleNavegacaoComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('', []),
        modulo: new FormControl<string | number>(null, []),
    });

    constructor(
        public dialog: MatDialog,
        public navegacaoAtualService: NavegacaoAtualService,
    ) {
        super();
    }

    ngOnInit(): void {
        super.ngOnInit();
    }

    protected obterTitulo() {
        return 'Navegação';
    }

    protected async obterColunas() {
        return {
            ordem: 'Ordem',
            nome: 'Titulo',
            qtd_grupo_permissao: 'Qtd Grupos',
            qtd_usuario_grupo: 'Qtd Usuários',
            situacao: 'Situação',
        };
    }

    protected async obterDados(filtros: any) {
        if (!this.filtros.value.modulo) return { results: [] };
        return await apiPainelControleControleAcessoGruposMenus(filtros);
    }

    protected async obterFiltros() {
        return {
            ...this.filtros.value,
            id: this.filtros.value.modulo,
            modulo_id: this.filtros.value.modulo,
            modulo: this.filtros.value.modulo,
            pk: this.filtros.value.modulo,
            page: (this?.paginator?.pageIndex || 0) + 1,
            per_page: this?.paginator?.pageSize || 100000,
        };
    }

    protected irGrupoMenuCriar() {
        this.dialog.open(PainelControleNavegacaoGrupoMenuCriarComponent, {
            data: {
                onClose: () => this.atualizarListagemMenu(),
                modulo: this.filtros.value.modulo,
            },
        });
    }

    protected irGrupoMenuEditar(grupoMenu: { pk: number }) {
        this.dialog.open(PainelControleNavegacaoGrupoMenuEditarComponent, {
            data: {
                onClose: () => this.atualizarListagemMenu(),
                grupoMenuId: grupoMenu.pk,
            },
        });
    }

    protected irMenuCriar(grupoMenu: { pk: number }) {
        this.dialog.open(PainelControleNavegacaoMenuCriarComponent, {
            data: <PainelControleNavegacaoMenuCriarComponentData>{
                onClose: () => this.atualizarListagemMenu(),
                grupoMenuId: grupoMenu.pk,
            },
        });
    }

    protected irMenuListarUsuarios(menuConfig: { pk: number }) {
        this.dialog.open(PainelControleNavegacaoMenuListarUsuariosComponent, {
            data: <PainelControleNavegacaoMenuListarUsuariosComponentData>{
                onClose: () => this.atualizarListagemMenu(),
                menuId: menuConfig.pk,
            },
            width: '60%',
        });
    }

    protected irMenuEditar(menuConfig: { pk: number }) {
        this.dialog.open(
            PainelControleNavegacaoMenuEditarConfiguracaoComponent,
            {
                data: <
                    PainelControleNavegacaoMenuEditarConfiguracaoComponentData
                >{
                    onClose: () => this.atualizarListagemMenu(),
                    menuId: menuConfig.pk,
                },
            }
        );
    }

    protected irMenuGrupoEditar(menuConfig: { pk: number }) {
        this.dialog.open(PainelControleNavegacaoMenuEditarComponent, {
            data: <PainelControleNavegacaoMenuEditarComponentData>{
                onClose: () => this.atualizarListagemMenu(),
                menuId: menuConfig.pk,
            },
            width: '60%',
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

    selecaoModulos: MpmtSelecaoComponentConfiguracao = {
        obterFiltros: (payload) => {
            return {};
        },
        obterOpcoes: async (payload: any) => {
            const { results } = await apiPainelControleControleAcessoModulos(
                payload
            );

            const resultsFiltered = results.filter(
                (x) => x.situacao == 'ATIVO'
            );

            return { results: resultsFiltered };
        },
    };

    get moduloSelecionado() {
        return this.filtros.value.modulo;
    }


    atualizarListagemMenu(){
        this.aplicarFiltros();
        this.navegacaoAtualService.recarregar()

    }

}
