import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDiariasGruposAprovadores } from 'api/diarias/config/grupo-aprovador/api-grupos-aprovadores';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class DiariasGruposAprovadoresService extends MpmtListagem2Service {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        situacao: new FormControl<string>('ATIVO', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiDiariasGruposAprovadores(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
