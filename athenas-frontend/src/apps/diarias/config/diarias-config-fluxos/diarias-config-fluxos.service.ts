import { Injectable } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { apiDiariasConfigFluxosAtualizarOrdem } from 'api/diarias/config/api-diarias-config-fluxos-atualizar-ordem.service';
import { apiDiariasConfigFluxos } from 'api/diarias/config/api-diarias-config-fluxos.service';
import { MpmtPaginacao } from 'components/mpmt-celula/mpmt-celula.interface';
import { MpmtListagemReordenavelService } from 'components/mpmt-listagem-reordenavel/mpmt-listagem-reordenavel.service';
import { MpmtListagem2Linha } from 'components/mpmt-listagem2/mpmt-listagem2.interface';

@Injectable()
export class DiariasConfigFluxosService extends MpmtListagemReordenavelService {
    filtros = new FormGroup({
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiDiariasConfigFluxos(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    public async atualizarOrdem(dados: MpmtListagem2Linha[]): Promise<any> {
        const ordemAtualizada = dados.map((item, index) => ({
            id: item.id,
            novaOrdem: index + 1
        }));
        const payload = {
            updates: ordemAtualizada
        };
        return apiDiariasConfigFluxosAtualizarOrdem(payload);
    }

    protected async obterPaginacao(): Promise<MpmtPaginacao> {
        this.paginacao.per_page = null;
        return { ...this.paginacao };
    }

}
