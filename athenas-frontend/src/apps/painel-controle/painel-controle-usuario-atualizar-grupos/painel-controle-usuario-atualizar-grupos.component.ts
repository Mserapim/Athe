import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import {
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import {
    ApiPainelControleControleAcessoModulos,
    apiPainelControleControleAcessoModulos, ApiPainelControleControleAcessoModulosItem
} from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { apiPainelControleControleAcessUsuarioAtualizarGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-usuario-atualizar-grupos.service';
import { Payload, apiPainelControleControleAcessoUsuarioGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-usuario-grupos.service';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { SelectItem } from 'utils/select-item';
import { PainelControleUsuarioAtualizarGruposService } from './painel-controle-usuario-atualizar-grupos.service';
import { apiPainelControleControleAcessoGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos.service';

export class PainelControleUsuarioAtualizarGruposComponentData {
    onClose?: Function;
    usuario?: any;
}


@Component({
    selector: 'painel-controle-usuario-atualizar-grupos',
    templateUrl: 'painel-controle-usuario-atualizar-grupos.component.html',
    standalone: false
})
export class PainelControleUsuarioAtualizarGruposComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        modulo_id: new FormControl<string | number>(null, [])

    });

    lista1:SelectItem[] = [];
    lista2:SelectItem[] = [];

    lista1Retorno:any[] = []
    lista2Retorno:any[] = []

    modulos: ApiPainelControleControleAcessoModulosItem[] = [];

    totalItensLista1: number;

    nome:string = null

    constructor(
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleUsuarioAtualizarGruposComponentData,
        private ListaService: PainelControleUsuarioAtualizarGruposService
    ) {
        super();
    }

    protected obterTitulo() {
        return 'Grupo de permissão do usuário ';
    }

    protected async obterColunas() {
        return {
            nome: 'Nome',
        };
    }

    protected async carregarLista1(filtros:any){
        return await apiPainelControleControleAcessoGrupos(filtros);

    }

    protected async carregarLista2(filtros:any){
        return await apiPainelControleControleAcessoUsuarioGrupos(filtros);
    }

    protected async configurarDados() {
        const response1 = await this.carregarLista1(this.obterFiltro());
        const response2 = await this.carregarLista2(this.obterFiltroUsuario());
        this.ListaService.carregarDados(response1,response2)
        this.totalItensLista1 = response1.total;
        this.lista1 = this.ListaService.lista1
        this.lista2 = this.ListaService.lista2
        this.lista1Retorno = this.ListaService.lista1Retorno
        this.lista2Retorno = this.ListaService.lista2Retorno
        this.carregarNome()
    }

    protected carregarNome() {
        this.nome = this.data.usuario.nome
    }

    protected obterFiltro() {
        return {
            ...this.filtros.value,
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
        };
    }

    protected obterFiltroUsuario() {
        return<Payload> {
            usuario_id:this.data.usuario.id,
        }
    }

    protected async atualizarUsuarioGrupos() {
        try {
            const lista_ids = this.lista2.map(item =>item.value)
            const {} = await apiPainelControleControleAcessUsuarioAtualizarGrupos(
                {
                    "servidor_id":this.data.usuario.id,
                    "usuario_grupos_ids":this.lista2Retorno
                }
            );
            this.data.onClose()
            this.dialog.closeAll();
        } catch (e: any) {
            console.log(e);

        }
    }

    protected async receberEvento1(dados: []){
        this.lista1Retorno = dados
    }

    protected async receberEvento2(dados:[]){
        this.lista2Retorno = dados
    }

    selecaoModulos: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: payload => {
            return apiPainelControleControleAcessoModulos({situacao: "ATIVO"});
        },
    };

    get moduloSelecionado() {
        return this.filtros.value.modulo_id;
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];

    async receberFiltroEvento1(filtro: any) {
        const response1 = await this.carregarLista1(filtro);
        this.lista1 = response1.results? response1.results.map(item => ({ label: item.nome, value: item.id })): []
    }
}
