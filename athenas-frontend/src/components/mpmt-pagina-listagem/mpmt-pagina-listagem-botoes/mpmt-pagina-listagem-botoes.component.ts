import { Component, Input } from '@angular/core';
import { MpmtPaginaListagemColuna } from '../mpmt-pagina-listagem.interface';
import { MpmtPaginaListagemService } from '../mpmt-pagina-listagem.service';

@Component({
    selector: 'mpmt-pagina-listagem-botoes',
    templateUrl: './mpmt-pagina-listagem-botoes.component.html',
    standalone: false,
})
export class MpmtPaginaListagemBotoesComponent {
    @Input('service') service?: MpmtPaginaListagemService;
    @Input('ajuda-url') ajudaUrl?: string;

    constructor() {}

    /** links */
    abrirAjuda() {
        if (this.ajudaUrl) window.open(this.ajudaUrl, '_blank');
    }

    trocarColunaVisibilidade(
        event: any,
        coluna: MpmtPaginaListagemColuna,
    ) {
        this.service.trocarColunaVisibilidade(coluna);
        event.stopPropagation();
        event.preventDefault();
    }
}
