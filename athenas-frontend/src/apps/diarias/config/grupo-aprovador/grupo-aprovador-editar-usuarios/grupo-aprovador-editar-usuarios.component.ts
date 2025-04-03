import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef} from '@angular/material/dialog';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { SelectItem } from 'utils/select-item';
import { DiariasGrupoAprovadorEditarUsuariosService } from './grupo-aprovador-editar-usuarios.service';
import { PayloadGrupoDiarias, apiDiariasGrupoAprovadorUsuarios } from 'api/diarias/config/grupo-aprovador/api-grupo-aprovador-usuarios';
import { apiDiariasGrupoAprovadorEditar } from 'api/diarias/config/grupo-aprovador/api-grupo-aprovador-editar';
import { apiDiariasUsuarios } from 'api/diarias/config/grupo-aprovador/api-usuarios';

export class DiariasGrupoAprovadorEditarUsuariosComponentData {
    onClose?: Function;
    grupo?: any;
    usuario_grupo?: any;
}


@Component({
    selector: 'grupo-aprovador-editar-usuarios',
    templateUrl: 'grupo-aprovador-editar-usuarios.component.html',
    standalone: false
})
export class DiariasGrupoAprovadorEditarUsuariosComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    lista1:SelectItem[] = [];
    totalItensLista1: number;
    lista2:SelectItem[] = [];

    lista1Retorno:any[] = []
    lista2Retorno:any[] = []

    nome:string = null
    id:number = null

    constructor(
        public dialogRef: MatDialogRef<DiariasGrupoAprovadorEditarUsuariosComponent>,
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasGrupoAprovadorEditarUsuariosComponentData,
        private ListaService: DiariasGrupoAprovadorEditarUsuariosService
    ) {
        super();
    }

    protected obterTitulo() {
        return 'Editar usuários de grupo de aprovadores';
    }

    protected async carregarLista1(filtros:any) {
        return await apiDiariasUsuarios(filtros);

    }

    protected async carregarLista2(filtros:any){
        return await apiDiariasGrupoAprovadorUsuarios(filtros);
    }

    protected async configurarDados() {
        const response1 = await this.carregarLista1(this.obterFiltro());
        const response2 = await this.carregarLista2(this.obterFiltroGrupo());
        this.ListaService.carregarDados(response1,response2)
        this.totalItensLista1 = response1.total;
        this.lista1 = this.ListaService.lista1
        this.lista2 = this.ListaService.lista2
        this.lista1Retorno = this.ListaService.lista1Retorno
        this.lista2Retorno = this.ListaService.lista2Retorno
        this.carregarNome()
    }

    protected obterFiltroGrupo() {
        if (this.data.grupo) {
            return<PayloadGrupoDiarias>{
                grupo_id:this.data.grupo.id,
            }
        } else {
            return<PayloadGrupoDiarias>{
                grupo_id:this.data.usuario_grupo.usuario_grupo,
            }
        }
    }

    protected obterFiltro() {
        return {
            ...this.filtros.value,
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 20,
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
            const {} = await apiDiariasGrupoAprovadorEditar(
                {
                    "id":this.id,
                    "servidores":this.lista2Retorno,
                    "nome":this.nome
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
