import { Injectable } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';

@Injectable({
    providedIn: 'root',
})
export class PaginaTituloAtualService {
    constructor(
        private navegacaoAtualService: NavegacaoAtualService,
        private titleService: Title
    ) {
        this.observarPaginaAtual();
    }

    /**
     */
    private async observarPaginaAtual() {
        this.navegacaoAtualService.paginaAtual$.subscribe(async (pagina) => {
            if (!pagina) return;

            this.titleService.setTitle(
                `${pagina?.nome} - ${pagina?.modulo?.nome}`
            );
        });
    }
}
