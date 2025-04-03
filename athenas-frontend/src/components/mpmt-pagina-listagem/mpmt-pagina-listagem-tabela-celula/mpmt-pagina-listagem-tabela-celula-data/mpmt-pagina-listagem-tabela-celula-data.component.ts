import { Component, Input } from '@angular/core';
import {
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
} from '../../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemTabelaCelulaComponent } from '../mpmt-pagina-listagem-tabela-celula.component';
import moment from 'moment';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula-data',
    templateUrl: './mpmt-pagina-listagem-tabela-celula-data.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaCelulaDataComponent extends MpmtPaginaListagemTabelaCelulaComponent {
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        super(navegacaoAtualService);
    }

    formatarData(data) {
        return data ? moment(data).format('DD/MM/YYYY') : '';
    }

}
