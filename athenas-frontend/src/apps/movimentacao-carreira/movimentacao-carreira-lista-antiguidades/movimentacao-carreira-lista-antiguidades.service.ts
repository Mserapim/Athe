import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiRhListaAntiguidades } from 'api/rh/api-rh-lista-antiguidades.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class MovimentacaoCarreiraListaAntiguidadesService extends MpmtListagem2Service {
    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        palavra_chave: new FormControl<string>('', []),
        tipo_membro: new FormControl<number>(0, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiRhListaAntiguidades(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}