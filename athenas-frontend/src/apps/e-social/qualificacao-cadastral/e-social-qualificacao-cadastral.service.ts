import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import {apiESocialListarItensTabela} from "../../../api/esocial/api-esocial-listar-itens-tabela.service";
import {
    apiESocialListarQualificacaoCadastral
} from "../../../api/esocial/api-esocial-listar-qualificacao-cadastral.service";

@Injectable()
export class ESocialQualificacaoCadastralService extends MpmtListagem2Service {
    filtros = new FormGroup({
        'categoria[]': new FormControl<number[]>(null, []),
        'status[]': new FormControl<number[]>(null, []),
        'orientacao_nis[]': new FormControl<number[]>(null, []),
        'orientacao_cpf[]': new FormControl<number[]>(null, []),
        keyword: new FormControl<string>('', [])
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiESocialListarQualificacaoCadastral(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
