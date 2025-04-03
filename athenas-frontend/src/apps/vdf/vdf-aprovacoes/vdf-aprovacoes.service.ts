import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiPainelControleControleAcessoGrupos } from 'api/painel-controle/api-painel-controle-controle-acesso-grupos.service';
import { apiPainelControleControleAcessoModulos } from 'api/painel-controle/api-painel-controle-controle-acesso-modulos.service';
import { apiRhPvfApprovalsRequests } from 'api/rh/api-rh-pvf-approvals-requests.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { formatDate } from 'utils/format-date';

@Injectable()
export class VdfAprovacoesService extends MpmtListagem2Service {
    filtros = new FormGroup({
        keyword: new FormControl<string>(null, []),
        approvals: new FormControl<string>(null, []),
        employe_types: new FormControl<string>(null, []),
        request_type: new FormControl<string>(null, []),
        status: new FormControl<string>(null, []),
        pending_request: new FormControl<string>(null, []),
        data_inicio: new FormControl<Date>(null, []),
        data_fim: new FormControl<Date>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return apiRhPvfApprovalsRequests(filtros);
    }

    protected async obterFiltros() {
        const dt_inicio_value = this.filtros.get('data_inicio')?.value;
        const dt_fim_value = this.filtros.get('data_fim')?.value;
        const dt_inicio = formatDate(dt_inicio_value);
        const dt_fim = formatDate(dt_fim_value);
        return {
            ...this.filtros.value,
            data_inicio: dt_inicio,
            data_fim: dt_fim,
        };
    }

    protected get downloadCsvSincrono() {
        return false;
    }
}
