import { Component, Input } from '@angular/core';
import {
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
} from '../../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemTabelaCelulaComponent } from '../mpmt-pagina-listagem-tabela-celula.component';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula-texto',
    templateUrl: './mpmt-pagina-listagem-tabela-celula-texto.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaCelulaTextoComponent extends MpmtPaginaListagemTabelaCelulaComponent {
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        super(navegacaoAtualService);
    }


    protected obterValor(
        coluna: MpmtPaginaListagemColuna,
        linha: MpmtPaginaListagemLinha
    ) {
        const valor = super.obterValor(coluna, linha) || "";
        if (coluna.limitar_caracteres && valor.length > 26) {
            return valor.substring(0, 26) + (valor.length > 26 ? '...' : '');
        }
        return valor;
    }
}
