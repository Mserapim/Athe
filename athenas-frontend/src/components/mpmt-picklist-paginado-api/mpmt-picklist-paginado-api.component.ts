import { Component, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { MatSelectionList } from '@angular/material/list';
import { SelectItem } from "../../utils/select-item";
import {PageEvent} from "@angular/material/paginator";
import { HttpClient } from "@angular/common/http";
import {
    apiPainelControleControleAcessoUsuarios
} from "../../api/painel-controle/api-painel-controle-controle-acesso-usuarios.service";

@Component({
    selector: 'mpmt-picklist-paginado-api',
    templateUrl: './mpmt-picklist-paginado-api.component.html',
    styleUrls: ['./mpmt-picklist-paginado-api.component.scss'],
    standalone: false
})
export class MpmtPicklistPaginadoApiComponent {
    @Input() textoLista1: string;
    @Input() textoLista2: string;
    @Input() _lista1: SelectItem[] = [];
    @Input()
    set lista1(lista1: SelectItem[]) {
        this._lista1 = lista1;
    }

    @Input() _lista2: SelectItem[] = [];
    @Input()
    set lista2(lista2: SelectItem[]) {
        this._lista2 = lista2;
        this.lista2Filtrada = this._lista2;
    }
    @Input() totalItems: number = 0;

    @Output() lista1Retorno = new EventEmitter<any[]>();
    @Output() lista2Retorno = new EventEmitter<any[]>();

    /* Os filtros selecionados serão enviados nesses EventEmitter.
    * implemente a chamada das apis no componente pai e envie os valores filtrados novamente na lista1 e lista2*/
    @Output() filtroLista1 = new EventEmitter<any>();
    @ViewChild('availableList') availableList: MatSelectionList;
    @ViewChild('selectedList') selectedList: MatSelectionList;

    todosSelecionados: boolean = false;
    todosSelecionados2: boolean = false;

    isLoadingLista1: boolean = false;  // Spinner para Lista 1
    isLoadingLista2: boolean = false;  // Spinner para Lista 2

    pageSize: number = 10;
    searchLeftTerm: string = null;
    searchRightTerm: string = '';
    lista2Filtrada: SelectItem[] = []

    constructor(private http: HttpClient) {}

    ngOnInit(): void {
        this.loadLeftItems();
    }

    async loadLeftItems(pageIndex: number = 1) {
        this.isLoadingLista1 = true
        let filtro = {
            palavra_chave: this.searchLeftTerm,
            page: pageIndex,
            per_page: this.pageSize,
            situacao: 'Ativo'
        };
        this.filtroLista1.emit(filtro);
        // const response1 = await apiPainelControleControleAcessoUsuarios(filtro);
        // this._lista1 = response1.results.map(item => ({ label: item.nome, value: item.id }));
        this.isLoadingLista1 = false;
    }

    onPageChange(event: PageEvent): void {
        this.loadLeftItems(event.pageIndex + 1);
    }

    searchLeft(term: string): void {
        this.searchLeftTerm = term;
        this.loadLeftItems();
    }

    searchRight(): void {
        this.isLoadingLista2
        this.lista2Filtrada = this._lista2.filter(item => item.label.toUpperCase().includes(this.searchRightTerm.toUpperCase()));
        this.isLoadingLista2
    }

    addToRight(): void {
        const selectedValues = this.availableList.selectedOptions.selected.map((option) => option.value);

        selectedValues.forEach(selected => {
            if (!this.isSelected(selected)) {
                this._lista2.push(selected);
            }
        })

        this.searchRight();
        this.emitChanges();
    }

    removeFromRight(): void {
        const selectedValues = this.selectedList.selectedOptions.selected.map((option) => option.value);
        this._lista2 = this._lista2.filter(item => !selectedValues.includes(item));
        this.searchRight();
        this.emitChanges();

        this.desmarcarTodos();
    }

    isSelected(item: any): boolean {
        return this._lista2.filter(itemLista2 => itemLista2.value == item.value).length > 0;
    }

    private emitChanges() {
        this.lista1Retorno.emit(this._lista1.map(item => item.value));
        this.lista2Retorno.emit(this._lista2.map(item => item.value));
    }

    desmarcarTodos(){
        //TODO - verificar uma forma melhor de desmarcar os itens
        setTimeout(() => {
            this.selectedList.deselectAll();
            this.availableList.deselectAll();
        }, 100);
    }

    marcarDesmarcarTodos(lista: string) {
        if(lista === 'availableList') {
            this.todosSelecionados = !this.todosSelecionados;
        } else if (lista === 'selectedList') {
            this.todosSelecionados2 = !this.todosSelecionados2;
        }

        if (this.todosSelecionados || this.todosSelecionados2) {
            this.marcarLista(lista);
        } else {
            this.desmarcarLista(lista);
        }
    }


    marcarLista(lista: string) {
        if(lista === 'selectedList') {
            this.selectedList.selectAll();
        } else if (lista === 'availableList') {
            this.availableList.selectAll();
        }
    }

    desmarcarLista(lista: string) {
        if(lista === 'selectedList') {
            this.selectedList.deselectAll();
        } else if (lista === 'availableList') {
            this.availableList.deselectAll();
        }
    }
}
