import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { MpmtListagemComponent } from 'components/mpmt-listagem/mpmt-listagem.component';
import { SelectItem } from 'utils/select-item';
import {apiRhSevidoresService} from "../../../../../api/rh/api-rh-servidores.service";
import {VincularServidoresDialogService} from "./vincular-servidores-dialog.service";
import {apiRhSevidorService} from "../../../../../api/rh/api-rh-servidor.service";
import {apiRhCategoriaFuncional} from "../../../../../api/rh/api-rh-categoria-funcional.service";
import {MpmtSelecaoComponentConfiguracao} from "../../../../../components/mpmt-selecao/mpmt-selecao.component";

export class VincularServidoresDialogComponentData {
    form: FormGroup;
}


@Component({
    selector: 'vincular-servidores-dialog',
    templateUrl: 'vincular-servidores-dialog.component.html',
    standalone: false
})
export class VincularServidoresDialogComponent extends MpmtListagemComponent {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', [])
    });

    lista1:SelectItem[] = [];
    totalItensLista1: number;
    lista2:SelectItem[] = [];

    lista1Retorno:any[] = []
    lista2Retorno:any[] = []

    nome:string = null
    id:number = null;

    form: FormGroup;

    servidor: any = null;

    situacao = true;
    situacoes = [{value: true, label: "Ativo"}, {value: false, label: "Inativo"}]

    selecaoCatFuncional: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhCategoriaFuncional,
        obterValor: 'cod',
    };

    categoriaFuncional: any;

    filtro: {
        palavra_chave: string,
        page: number,
        per_page: number,
        situacao: boolean,
        tipo_posse: string[]
    }

    private textoFiltro = "";

    constructor(
        public dialogRef: MatDialogRef<VincularServidoresDialogComponent>,
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        protected data: VincularServidoresDialogComponentData,
        private ListaService: VincularServidoresDialogService
    ) {
        super();
        this.form = data.form;
    }

    protected obterTitulo() {
        return 'Permissão grupo usuário';
    }

    protected async carregarLista1(filtros:any) {
        return await apiRhSevidoresService(filtros);
    }

    protected async carregarLista2(){
        let servidoresSelecionados = [];
        let idServidoresSelecionados = this.form.value.servidores_gerados_ids;
        for (const idServidor of idServidoresSelecionados) {
            this.servidor = await apiRhSevidorService({id:idServidor});
            servidoresSelecionados.push({value: this.servidor.pk, label: this.servidor.nome} as SelectItem)
        }
        return servidoresSelecionados;
    }

    protected async configurarDados() {
        const response1 = await this.carregarLista1(this.obterFiltro());
        const response2 = await this.carregarLista2();
        await this.ListaService.carregarDados(response1,response2)
        this.lista1 = this.ListaService.lista1
        this.lista2 = this.ListaService.lista2
        this.totalItensLista1 = response1.total;
        this.lista1Retorno = this.ListaService.lista1Retorno
        this.lista2Retorno = this.ListaService.lista2Retorno
    }

    protected obterFiltro() {
        return {
            ...this.filtros.value,
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
            situacao:'Ativo'
        };
    }


    protected async receberEvento1(dados: []){
        this.lista1Retorno = dados
    }

    protected async receberEvento2(dados:[]){
        this.lista2Retorno = dados
    }

    async receberFiltroEvento1(filtro: any) {
        this.filtro = filtro;
        this.filtrar()
    }

    async filtrar() {
        this.filtro.situacao = this.situacao
        this.filtro.tipo_posse = this.categoriaFuncional

        const response1 = await this.carregarLista1(this.filtro);
        this.lista1 = response1.results ? response1.results.map(item => ({label: item.nome, value: item.pk})) : []
        this.totalItensLista1 = response1.total;
    }

    salvar() {
        try {
            const lista_ids = this.lista2.map(item =>item.value)
            this.form.patchValue({
                servidores_gerados_ids: lista_ids
            })

            this.dialogRef.close();
        } catch (e: any) {
            console.log(e);

        }
    }
}
