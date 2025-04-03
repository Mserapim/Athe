import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleTiposClasscode } from 'api/painel-controle/api-painel-controle-classcode-tipo.service';
import { apiPainelControleClasscodes } from 'api/painel-controle/api-painel-controle-classcodes.service';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';

@Injectable()
export class ClasscodesService extends MpmtListagemService {
    public loading: boolean = false;

    tipos: { sigla: string; texto: string }[] = [];

    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        keyword: new FormControl<string>('', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        this.loading = true;
        const dados = await apiPainelControleClasscodes(filtros);
        this.loading = false;
        return dados;
    }

    protected async obterFiltros() {
        return { ...this.filtros.value, id:this.selecionada};
    }

    protected get downloadCsvSincrono() {
        return false;
    }

    public async carregarTiposClasscode() {
        try {
            this.tipos = (await apiPainelControleTiposClasscode({})).results;
        } catch (error) {
            console.error('Erro ao carregar os tipos de classcode:', error);
        }
    }

    get itemSelecionado() {
        return this.obterItensSelecionados().length > 0 
    }
}
