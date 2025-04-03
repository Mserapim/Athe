import { Component, Input, OnChanges } from '@angular/core';
import {
    MpmtPaginaListagemColuna,
    MpmtPaginaListagemLinha,
} from '../mpmt-pagina-listagem.interface';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';

@Component({
    selector: 'mpmt-pagina-listagem-tabela-celula',
    templateUrl: './mpmt-pagina-listagem-tabela-celula.component.html',
})
export abstract class MpmtPaginaListagemTabelaCelulaComponent
    implements OnChanges
{
    @Input('coluna') coluna?: MpmtPaginaListagemColuna;
    @Input('linha') linha?: MpmtPaginaListagemLinha;

    protected valor = null as any;
    protected estilo = '';
    protected acoesPermitidas: { [key: string]: boolean } = {};

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        this.observarPermissoes();
    }

    /** Ciclo de vida */
    ngOnChanges() {
        if (!this.coluna) return;
        if (!this.linha) return;

        this.valor = this.obterValor(this.coluna, this.linha);
        this.estilo = this.obterEstilo(this.coluna, this.linha);
    }

    /** private */
    private observarPermissoes() {
        this.navegacaoAtualService.acoes$.subscribe((acoes: string[]) => {
            if (!acoes) return;
            this.acoesPermitidas = {};
            for (const acao of acoes) {
                this.acoesPermitidas[acao] = acoes.includes(acao);
            }
        });
    }

    /** Protected */
    protected obterValor(
        coluna: MpmtPaginaListagemColuna,
        linha: MpmtPaginaListagemLinha
    ) {
        if (!coluna) return;
        if (!linha) return;
        const valor = this.linha[this.coluna.codigo];
        if (!this.coluna.transformarValor) return valor;
        return this.coluna.transformarValor(this.linha);
    }

    protected obterEstilo(
        coluna: MpmtPaginaListagemColuna,
        linha: MpmtPaginaListagemLinha
    ) {
        if (!coluna.construirEstilo) return '';
        return coluna.construirEstilo(linha);
    }
}
