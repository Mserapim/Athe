import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiDefinColaboradoresEventuais } from 'api/defin/colaborador-eventual/api-defin-colaboradores-eventuais.service';
import { MpmtListagem2AccordionService } from 'components/mpmt-listagem2-accordion/mpmt-listagem2-accordion.service';

@Injectable()
export class ColaboradorEventualService extends MpmtListagem2AccordionService {
    filtros = new FormGroup({
        order_by: new FormControl<string>(null, []),
        palavra_chave: new FormControl<string>('', []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiDefinColaboradoresEventuais(filtros);
    }

    protected async obterFiltros() {
        return { ...this.filtros.value };
    }
}