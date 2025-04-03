import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import {apiESocialListarItensTabela} from "../../../api/esocial/api-esocial-listar-itens-tabela.service";
import {
    MpmtListagem2AccordionService
} from "../../../components/mpmt-listagem2-accordion/mpmt-listagem2-accordion.service";

@Injectable()
export class ESocialItensTabelaService extends MpmtListagem2AccordionService {
    filtros = new FormGroup({
        tabela: new FormControl<number>(null, []),
        keyword: new FormControl<string>('', [])
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiESocialListarItensTabela(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}
