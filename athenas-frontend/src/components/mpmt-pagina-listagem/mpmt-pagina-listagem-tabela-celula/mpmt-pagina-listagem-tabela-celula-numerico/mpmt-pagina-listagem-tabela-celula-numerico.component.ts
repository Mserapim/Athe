import { Component, Input } from '@angular/core';
import {
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
} from '../../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemTabelaCelulaTextoComponent } from '../mpmt-pagina-listagem-tabela-celula-texto/mpmt-pagina-listagem-tabela-celula-texto.component';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula-numerico',
    templateUrl: './mpmt-pagina-listagem-tabela-celula-numerico.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaCelulaNumericoComponent extends MpmtPaginaListagemTabelaCelulaTextoComponent {
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        super(navegacaoAtualService);
    }
}
