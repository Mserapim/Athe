import { Component, Input } from '@angular/core';
import { MpmtPaginaListagemColuna, MpmtPaginaListagemLinha } from '../../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemTabelaCelulaComponent } from '../mpmt-pagina-listagem-tabela-celula.component';
import moment from 'moment';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula-data-hora',
    templateUrl: './mpmt-pagina-listagem-tabela-celula-data-hora.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaCelulaDataHoraComponent extends MpmtPaginaListagemTabelaCelulaComponent {
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        super(navegacaoAtualService);
    }

    formatarDataHora(data: string | Date): string {
        return data ? moment(data).locale('pt-br').format('DD/MM/YYYY HH:mm:ss') : '';
    }

}
