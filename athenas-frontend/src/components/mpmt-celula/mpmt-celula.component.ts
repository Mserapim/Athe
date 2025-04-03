import { Component, Input, OnChanges } from '@angular/core';
import {
    MpmtColuna,
    MpmtLinha,
} from './mpmt-celula.interface';
import { BehaviorSubject } from 'rxjs';
import moment from 'moment';
import { NavegacaoAtualService } from 'core/navegacao-atual/navegacao-atual.service';
@Component({
    selector: 'mpmt-celula',
    templateUrl: './mpmt-celula.component.html',
    styleUrls: ['./mpmt-celula.component.scss'],
    standalone: false
})
export class MpmtCelulaComponent implements OnChanges {
    @Input('coluna') coluna: MpmtColuna;
    @Input('linha') linha: MpmtLinha;
    @Input('estaSelecionada') estaSelecionada: (element: any) => boolean;
    @Input('toggleSelecao') toggleSelecao: (element: any, event: any) => void;

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

    contruirValor(coluna: MpmtColuna, linha: MpmtLinha) {

        if (!coluna) return;
        if (!linha) return;
        const valor = this.linha[this.coluna.codigo];
        
        if (!this.coluna.transformarValor) return valor;
        return this.coluna.transformarValor(linha);
    }

    formatarData = (data) => {
        return data ? moment(data).format('DD/MM/YYYY') : '';
    };

    formatarDataHora = (data) => {
        return data ? moment(data).format('DD/MM/YYYY HH:mm') : '';
    };
    formatarBooleano = (valor: boolean) => valor ? 'Sim' : 'Não';
    formatarMoeda = (valor: number) => valor != null ? `R$ ${valor.toFixed(2).replace('.', ',')}` : '';

    protected acaoVisivel(acao: any, linha: MpmtLinha) {
        try {
            return acao?.exibirSe(linha);
        } catch {
            return true;
        }
    }

    protected acaoPermitida(acao: any, linha: MpmtLinha) {
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

    public getVisibleAcoes(acoes: any[], linha: MpmtLinha): any[] {
        return (
            acoes?.filter((acao) => {
                return (
                    this.acaoVisivel(acao, linha) &&
                    this.acaoPermitida(acao, this.linha)
                );
            }) || []
        );
    }
}
