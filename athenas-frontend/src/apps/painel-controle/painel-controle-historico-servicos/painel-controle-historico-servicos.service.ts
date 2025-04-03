import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleHistoricoServicos } from 'api/painel-controle/api-painel-controle-historico-servicos.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';

@Injectable()
export class PainelControleHistoricoServicosService extends MpmtListagem2Service {
    filtros = new FormGroup({
        keyword: new FormControl<string>('', []),
        executado: new FormControl<string>(null, []),
        servico_id: new FormControl<number>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiPainelControleHistoricoServicos(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }

    limparFiltros() {
        this.filtros.reset();
    }
}
