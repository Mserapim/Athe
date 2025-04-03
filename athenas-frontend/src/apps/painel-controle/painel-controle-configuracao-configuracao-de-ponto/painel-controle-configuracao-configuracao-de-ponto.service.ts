import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControlConfigPonto } from 'api/painel-controle/api-painel-controle-configuracao-configuracao-de-ponto.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class PainelControleConfigPontoService extends MpmtListagem2Service {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiPainelControlConfigPonto(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

}
