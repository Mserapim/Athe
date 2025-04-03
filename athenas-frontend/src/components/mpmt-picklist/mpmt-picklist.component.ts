import { Component, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { MatSelectionList } from '@angular/material/list';
import { SelectItem } from "../../utils/select-item";

@Component({
    selector: 'mpmt-picklist',
    templateUrl: './mpmt-picklist.component.html',
    styleUrls: ['./mpmt-picklist.component.scss'],
    standalone: false
})
export class MpmtPicklistComponent {
    @Input() textoLista1: string;
    @Input() textoLista2: string;
    @Input() lista1: SelectItem[] = [];
    @Input() lista2: SelectItem[] = [];
    @Output() lista1Retorno = new EventEmitter<any[]>();
    @Output() lista2Retorno = new EventEmitter<any[]>();

    @ViewChild('availableList') availableList: MatSelectionList;
    @ViewChild('selectedList') selectedList: MatSelectionList;

    availableSearch: string = '';
    selectedSearch: string = '';

    todosSelecionados: boolean = false;
    todosSelecionados2: boolean = false;

    constructor() {
        this.desmarcarTodos();
    }

    marcarDesmarcarTodos(lista: string) {
        this.todosSelecionados = !this.todosSelecionados;
        if (this.todosSelecionados) {
            this.marcarLista(lista);
        } else {
            this.desmarcarLista(lista);
        }
    }

    addItem() {
        const selectedValues = this.availableList.selectedOptions.selected.map((option) => option.value);
        this.lista2.push(...selectedValues);
        this.lista1 = this.lista1.filter(item => !selectedValues.includes(item));
        this.emitChanges();

        this.desmarcarTodos();
    }

    removeItem() {
        const selectedValues = this.selectedList.selectedOptions.selected.map((option) => option.value);
        this.lista1.push(...selectedValues);
        this.lista2 = this.lista2.filter(item => !selectedValues.includes(item));
        this.emitChanges();

        this.desmarcarTodos();
    }

    addAllItems() {
        this.lista2.push(...this.lista1);
        this.lista1 = [];
        this.emitChanges();

        this.desmarcarTodos();
    }

    removeAllItems() {
        this.lista1.push(...this.lista2);
        this.lista2 = [];
        this.emitChanges();

        this.desmarcarTodos();
    }

    filterAvailableItems() {
        return this.lista1.filter(item =>
            item.label.toLowerCase().includes(this.availableSearch.toLowerCase())
        );
    }

    filterSelectedItems() {
        return this.lista2.filter(item =>
            item.label.toLowerCase().includes(this.selectedSearch.toLowerCase())
        );
    }

    desmarcarTodos(){
        //TODO - verificar uma forma melhor de desmarcar os itens
        setTimeout(() => {
            this.selectedList.deselectAll();
            this.availableList.deselectAll();
        }, 100);
    }

    private emitChanges() {
        this.lista1Retorno.emit(this.lista1.map(item => item.value));
        this.lista2Retorno.emit(this.lista2.map(item => item.value));
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
