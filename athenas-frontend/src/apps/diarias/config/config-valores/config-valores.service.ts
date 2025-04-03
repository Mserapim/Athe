import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasConfigValores } from 'api/diarias/config/api-diarias-config-valores.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class DiariasConfigValoresService extends MpmtListagem2Service {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiDiariasConfigValores(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
