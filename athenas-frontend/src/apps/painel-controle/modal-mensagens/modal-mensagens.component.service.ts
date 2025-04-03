import { Injectable, Input } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleMensagens } from 'api/painel-controle/api-painel-controle-mensagens.service';
import { MpmtListagemService } from 'components/mpmt-listagens/mpmt-listagem.service';

@Injectable()
export class MensagensService extends MpmtListagemService {
    public loading: boolean = false;
    private dadosListagem: any[] = [];

    filtros = new FormGroup({
        id: new FormControl<number>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        if (filtros?.id == null) {
            return null
        }
        this.loading = true;
        const dados = await apiPainelControleMensagens(filtros);
        this.dadosListagem = dados.results ?? []; 
        this.loading = false;
        return dados;
    }

    public obterListagem(): any[] {
        return this.dadosListagem ?? [];
    }

    protected async obterFiltros() {
        return { ...this.filtros.value, id:this.selecionada};
    }

    protected get downloadCsvSincrono() {
        return false;
    }

}
