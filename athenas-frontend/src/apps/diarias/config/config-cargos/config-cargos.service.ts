import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasConfigCargos } from 'api/diarias/config/api-diarias-config-cargos.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class DiariasConfigCargosService extends MpmtListagem2Service {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiDiariasConfigCargos(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
