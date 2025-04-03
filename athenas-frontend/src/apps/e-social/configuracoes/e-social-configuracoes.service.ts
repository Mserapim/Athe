import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import {apiESocialListarConfiguracoes} from "../../../api/esocial/api-esocial-listar-configuracoes.service";

@Injectable()
export class ESocialConfiguracoesService extends MpmtListagem2Service {
    filtros = new FormGroup({
        keyword: new FormControl<string>('', [])
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiESocialListarConfiguracoes(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
