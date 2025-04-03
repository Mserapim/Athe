import { Component, Input } from '@angular/core';
import {
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
} from '../../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemTabelaCelulaComponent } from '../mpmt-pagina-listagem-tabela-celula.component';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula-boleano-icone',
    templateUrl: './mpmt-pagina-listagem-tabela-celula-boleano-icone.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaCelulaBoleanoIconeComponent extends MpmtPaginaListagemTabelaCelulaComponent {
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        super(navegacaoAtualService);
    }

}
