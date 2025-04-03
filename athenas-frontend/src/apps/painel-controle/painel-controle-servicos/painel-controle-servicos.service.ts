import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleServicos } from 'api/painel-controle/api-painel-controle-servicos.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class PainelControleServicosService extends MpmtListagem2Service {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', []),
        executado: new FormControl<string>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiPainelControleServicos(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    limparFiltros() {
        this.filtros.reset();
    }
}
