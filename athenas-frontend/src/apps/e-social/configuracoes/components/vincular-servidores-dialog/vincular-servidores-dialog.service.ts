import { Injectable } from '@angular/core';
import { MpmtPickListService } from 'components/mpmt-picklist/mpmt-picklist.service';

@Injectable({
  providedIn: 'root'
})
export class VincularServidoresDialogService extends MpmtPickListService {

    constructor() {
        super()
    }

    async carregarListas(response1,response2) {
        const grupos1 = response1.results ? response1.results : []
        const lista1 = grupos1.map(item => ({ label: item.nome, value: item.id }));
        this.lista2 = response2;
        this.lista1 = lista1.filter(item1 => !this.lista2.some(item2 => item1.value === item2.value));
    }
}
