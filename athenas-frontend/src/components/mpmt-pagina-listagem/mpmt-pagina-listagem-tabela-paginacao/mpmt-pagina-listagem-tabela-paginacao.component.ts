import { Component, Input, OnChanges, ViewChild } from '@angular/core';
import { MpmtPaginaListagemService } from '../mpmt-pagina-listagem.service';
import { Paginator } from 'primeng/paginator';

interface PageEvent {
    first: number;
    rows: number;
    page: number;
    pageCount: number;
}


@Component({
    selector: 'mpmt-pagina-listagem-tabela-paginacao',
    templateUrl: './mpmt-pagina-listagem-tabela-paginacao.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaPaginacaoComponent implements OnChanges {
    @Input('page') page?: number;
    @Input('perPage') perPage?: number;
    @Input('service') service?: MpmtPaginaListagemService;
    @ViewChild('paginator') paginator: Paginator;

    first: number = 0;

    constructor() {}

    ngOnChanges() {
        if(this.page) {
            this.first = (this.page - 1) * this.perPage
        }
    }

    onPageChange(event: PageEvent) {
        this.service.paginacao.page = event.page + 1
        this.service.paginacao.per_page = event.rows 
        this.service.recarregarUmaVez();
    }

}
