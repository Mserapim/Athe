import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { apiPainelControleControleAcessoUsuarios } from 'api/painel-controle/api-painel-controle-controle-acesso-usuarios.service';
import { PayloadGrupoUsuario, apiPainelControleControleAcessoGrupoUsuarios } from 'api/painel-controle/api-painel-controle-controle-acesso-grupo-usuarios.service';
import { apiPainelControleControleAcessGrupoAtualizarUsuarios } from 'api/painel-controle/api-painel-controle-controle-acesso-grupo-atualizar-usuarios.service';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { SelectItem } from 'utils/select-item';
import { PainelControleGrupoAtualizarUsuariosService } from './painel-controle-grupo-atualizar-usuarios.service';
import {
    apiPainelControleControleAcessoUsuariosMinimo
} from "../../../api/painel-controle/api-painel-controle-controle-acesso-usuarios-minimo.service";

export class PainelControleGrupoAtualizarUsuariosComponentData {
    onClose?: Function;
    grupo?: any;
    usuario_grupo?: any;
}


@Component({
    selector: 'painel-controle-grupo-atualizar-usuarios',
    templateUrl: 'painel-controle-grupo-atualizar-usuarios.component.html',
    standalone: false
})
export class PainelControleGrupoAtualizarUsuariosComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        modulo_id: new FormControl<string | number>(null, [])

    });

    lista1:SelectItem[] = [];
    totalItensLista1: number;
    lista2:SelectItem[] = [];

    lista1Retorno:any[] = []
    lista2Retorno:any[] = []

    nome:string = null
    id:number = null

    constructor(
        public dialogRef: MatDialogRef<PainelControleGrupoAtualizarUsuariosComponent>,
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleGrupoAtualizarUsuariosComponentData,
        private ListaService: PainelControleGrupoAtualizarUsuariosService
    ) {
        super();
    }

    protected obterTitulo() {
        return 'Permissão grupo usuário';
    }

    protected async carregarLista1(filtros:any) {
        return await apiPainelControleControleAcessoUsuarios(filtros);

    }

    protected async carregarLista2(filtros:any){
        return await apiPainelControleControleAcessoUsuariosMinimo(filtros);
    }

    protected async configurarDados() {
        const response1 = await this.carregarLista1(this.obterFiltro());
        const response2 = await this.carregarLista2(this.obterFiltroGrupo());
        this.ListaService.carregarDados(response1,response2)
        this.lista1 = this.ListaService.lista1
        this.lista2 = this.ListaService.lista2
        this.totalItensLista1 = response1.total;
        this.lista1Retorno = this.ListaService.lista1Retorno
        this.lista2Retorno = this.ListaService.lista2Retorno
        this.carregarNome()
    }

    protected obterFiltroGrupo() {
        if (this.data.grupo) {
            return<PayloadGrupoUsuario>{
                usuario_grupo_id:this.data.grupo.id,
            }
        } else {
            return<PayloadGrupoUsuario>{
                usuario_grupo_id:this.data.usuario_grupo.usuario_grupo,
            }
        }
    }

    protected obterFiltro() {
        return {
            ...this.filtros.value,
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
            situacao:'Ativo'
        };
    }

    protected carregarNome() {
        if (this.data.grupo){
            this.nome = this.data.grupo.nome
        } else {
            this.nome = this.data.usuario_grupo.usuario_grupo_nome
        }
    }

    protected async atualizarGrupoUsuarios() {
        try {
            const lista_ids = this.lista2.map(item =>item.value)
            if (this.data.grupo) {
                this.id = this.data.grupo.id
            } else {
                this.id = this.data.usuario_grupo.usuario_grupo
            }
            const {} = await apiPainelControleControleAcessGrupoAtualizarUsuarios(
                {
                    "id":this.id,
                    "servidores":this.lista2Retorno
                }
            );
            this.data.onClose()
            this.dialogRef.close();
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

    async receberFiltroEvento1(filtro: any) {
        const response1 = await this.carregarLista1(filtro);
        this.lista1 = response1.results? response1.results.map(item => ({ label: item.nome, value: item.id })): []
    }
}
