import { Component, Input } from '@angular/core';
import {
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
} from '../../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
import { MpmtPaginaListagemTabelaCelulaComponent } from '../mpmt-pagina-listagem-tabela-celula.component';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula-objeto',
    templateUrl: './mpmt-pagina-listagem-tabela-celula-objeto.component.html',
    standalone: false,
})
export class MpmtPaginaListagemTabelaCelulaObjetoComponent extends MpmtPaginaListagemTabelaCelulaComponent {
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        super(navegacaoAtualService);
    }

    formatar(data: any) {
        if (!data) return '';
        
        // Se data é string retorna string
        if (typeof data === 'string') {
            return data;
        }
    
        // Se data é um objeto
        if (typeof data === 'object') {
            // Se tem atributo display
            if ('display' in data) {
                return data.display;
            }
            // Se tem atributo nome
            if ('nome' in data) {
                return data.nome;
            }
            // Se tem atributo label
            if ('label' in data) {
                return data.label;
            }
            
            // Se não, transforma o objeto em chave valor
            return Object.entries(data)
                .map(([key, value]) => `${key}: ${value}`)
                .join(', ');
        }
    
        return String(data);
    }

}
