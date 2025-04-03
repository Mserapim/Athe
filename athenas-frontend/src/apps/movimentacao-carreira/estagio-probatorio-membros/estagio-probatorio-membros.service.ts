import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiMembrosEstagioProbatorio } from 'api/rh/mov-carreira/api-membros-estagio-probatorio.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class EstagioProbatorioMembrosService extends MpmtListagem2Service {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiMembrosEstagioProbatorio(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}