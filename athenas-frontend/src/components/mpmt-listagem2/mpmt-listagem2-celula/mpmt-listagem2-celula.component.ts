import { Component, Input, OnChanges } from '@angular/core';
import {
    MpmtListagem2Coluna,
    MpmtListagem2Linha,
} from '../mpmt-listagem2.interface';
import { BehaviorSubject } from 'rxjs';
import moment from 'moment';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';

@Component({
    selector: 'mpmt-listagem2-celula',
    templateUrl: './mpmt-listagem2-celula.component.html',
    standalone: false
})
export class MpmtListagem2CelulaComponent implements OnChanges {
    @Input('coluna') coluna: MpmtListagem2Coluna;
    @Input('linha') linha: MpmtListagem2Linha;

    private valorSubject = new BehaviorSubject<
        string | number | boolean | Date
    >(undefined);
    public valor$ = this.valorSubject.asObservable();

    acoes: { [key: string]: boolean } = {};

    constructor(public navegacaoAtualService: NavegacaoAtualService) {
        this.observarPermissoes();
    }

    observarPermissoes() {
        this.navegacaoAtualService.acoes$.subscribe((acoes: string[]) => {
            if (!acoes) return;
            this.acoes = {};
            for (const acao of acoes) {
                this.acoes[acao] = acoes.includes(acao);
            }
        });
    }

    ngOnChanges() {
        if (!this.coluna) return;
        if (!this.linha) return;

        this.valorSubject.next(this.contruirValor(this.coluna, this.linha));
    }

    contruirValor(coluna: MpmtListagem2Coluna, linha: MpmtListagem2Linha) {
        if (!coluna) return;
        if (!linha) return;
        const valor = this.linha[this.coluna.codigo];
        if (!this.coluna.transformarValor) return valor;
        return this.coluna.transformarValor(this.linha);
    }

    formatarData = (data) => {
        return data ? moment(data).format('DD/MM/YYYY') : '';
    };

    formatarDataHora = (data) => {
        return data ? moment(data).format('DD/MM/YYYY HH:mm') : '';
    };
    formatarBooleano = (valor: boolean) => (valor ? 'Sim' : 'Não');

    protected acaoVisivel(acao: any, linha: MpmtListagem2Linha) {
        try {
            return acao?.exibirSe(linha);
        } catch {
            return true;
        }
    }

    protected acaoPermitida(acao: any, linha: MpmtListagem2Linha) {
        try {
            if (!acao.requerPermissao) return true;
            return this.acoes[acao.requerPermissao];
        } catch {
            return false;
        }
    }

    public temAcoesVisiveis(): boolean {
        return this.coluna.acoes?.some(
            (acao) =>
                this.acaoVisivel(acao, this.linha) &&
                this.acaoPermitida(acao, this.linha)
        );
    }

    public getVisibleAcoes(acoes: any[], linha: MpmtListagem2Linha): any[] {
        return (
            acoes?.filter((acao) => {
                return (
                    this.acaoVisivel(acao, linha) &&
                    this.acaoPermitida(acao, this.linha)
                );
            }) || []
        );
    }

    getIconeLinha(acoes: any[], linha: any): string | null {
        const acaoComIcone = acoes.find(
            (acao) => acao.icone_linha && acao.exibirSe && acao.exibirSe(linha)
        );
        return acaoComIcone ? acaoComIcone.icone : null;
    }

    construirEstilos(coluna: MpmtListagem2Coluna, linha: MpmtListagem2Linha) {
        if (!coluna.construirEstilo) return '';
        return coluna.construirEstilo(linha);
    }
}
