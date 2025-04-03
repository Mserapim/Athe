
import { Injectable } from '@angular/core';
import { SelectItem } from 'utils/select-item';

@Injectable({
  providedIn: 'root'
})
export class MpmtPickListService {
  
    lista1:SelectItem[] = [];
    lista2:SelectItem[] = [];

    lista1Retorno:any[] = []
    lista2Retorno:any[] = []

    constructor() { }

    async carregarDados(response1, response2) {
        this.carregarListas(response1,response2)
        this.carregarlistaRetorno()
    }
    
    async carregarListas(response1,response2) {
        const grupos1 = response1.results? response1.results: []
        const grupos2 = response2.results? response2.results: []
        const lista1 = grupos1.map(item => ({ label: item.nome, value: item.id }));
        this.lista2 = grupos2.map(item => ({ label: item.nome, value: item.id }));
        this.lista1 = lista1.filter(item1 => !this.lista2.some(item2 => item1.value === item2.value));
    }

    async carregarlistaRetorno() {
        this.lista1Retorno = this.lista1.map(item =>item.value)
        this.lista2Retorno = this.lista2.map(item =>item.value)
    }
}