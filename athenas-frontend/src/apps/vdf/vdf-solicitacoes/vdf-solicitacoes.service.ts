import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiRhPvfScalesServerShiftsService } from 'api/rh/api-rh-pvf-scales-server-shifts.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { pvfRequestsService } from 'services/pvf-requests.service';

@Injectable()
export class VdfSolicitacoesService extends MpmtListagem2Service {
    filtros = new FormGroup({
        keyword: new FormControl<string>(null, []),
        request_type: new FormControl<string>(null, []),
        status: new FormControl<string>(null, []),
        startDate: new FormControl<Date>(null, []),
        endDate: new FormControl<Date>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        return pvfRequestsService(filtros);
    }

    protected async obterFiltros() {
        return {
            ...this.filtros.value,
            startDate:
                this.filtros.value.startDate?.toISOString()?.substring(0, 10) ||
                undefined,
            endDate:
                this.filtros.value.endDate?.toISOString()?.substring(0, 10) ||
                undefined,
        };
    }
}
