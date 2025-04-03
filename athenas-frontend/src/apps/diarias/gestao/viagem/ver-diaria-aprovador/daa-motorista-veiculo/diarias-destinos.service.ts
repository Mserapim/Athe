import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasDestinos } from 'api/diarias/api-diarias-destinos.service';
import { MpmtPaginacao } from 'components/mpmt-celula/mpmt-celula.interface';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';
import { BehaviorSubject } from 'rxjs';

@Injectable()
export class DestinosService extends MpmtListagemService {
    public viagemID: number;
    public comMotorista: boolean;
    public veiculoDaa: boolean;

    filtros = new FormGroup({
        keyword: new FormControl<string>('', []),
    });

    private destinosSelecionadosDistintos$ = new BehaviorSubject<any[]>([]);

    constructor() {
        super();
    }

    async obterDados() {
        const destinos = await apiDiariasDestinos({
            viagem: this.viagemID,
            analise_daa: false,
            com_motorista: this.comMotorista,
            veiculo_daa: this.veiculoDaa,
        });
        return destinos;
    }

    protected async obterFiltros() {
        return { ...this.filtros.value, id:this.selecionada};
    }

    protected async obterPaginacao(): Promise<MpmtPaginacao> {
        this.paginacao.per_page = null;
        return { ...this.paginacao };
    }

    get destinosDistintos$() {
        return this.destinosSelecionadosDistintos$.asObservable();
    }

    adicionarItemSelecionado(item: any) {
        super.adicionarItemSelecionado(item);
        this.atualizarDestinosDistintos();
    }

    removerItemSelecionado(item: any) {
        super.removerItemSelecionado(item);
        this.atualizarDestinosDistintos();
    }

    private atualizarDestinosDistintos() {
        const itensSelecionados = this.obterItensSelecionados();
        const destinosUnicos = this.filtrarDestinosDistintos(itensSelecionados);
        destinosUnicos.sort((a, b) => new Date(a.data).getTime() - new Date(b.data).getTime());

        this.destinosSelecionadosDistintos$.next(destinosUnicos);
    }

    private filtrarDestinosDistintos(destinos: any[]): any[] {
        const destinosUnicos = new Map<string, any>();

        destinos.forEach((destino) => {
            const key = `${destino.uf_origem_display}-${destino.uf_destino_display}-${destino.data}`;
            if (!destinosUnicos.has(key)) {
                destinosUnicos.set(key, {
                    ...destino,
                    ids: [destino.id]
                });
            } else {
                destinosUnicos.get(key).ids.push(destino.id);
            }
        });

        return Array.from(destinosUnicos.values());
    }

}