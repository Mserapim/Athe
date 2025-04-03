import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { apiRhPvfScalesServerShiftsService } from 'api/rh/api-rh-pvf-scales-server-shifts.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { formatDate } from 'utils/format-date';

@Injectable()
export class VdfPlantoesService extends MpmtListagem2Service {
    public loading: boolean = false;

    public periodo = new FormGroup({
        end_date: new FormControl<Date | null>(null, []),
        start_date: new FormControl<Date | null>(null, []),
    });
    filtros = new FormGroup({
        keyword: new FormControl<string>(null, []),
        status: new FormControl<string>(null, []),
        start_date: new FormControl<Date>(null, []),
        lotacao_id: new FormControl<number>(null, []),
        cadastrado_por: new FormControl<string>("usuario_atual"),
        tipo_plantao: new FormControl<{ valor: number; titulo: string }[]>(
            [],
            []
        ),
        comarca_id: new FormControl<{ valor: number; titulo: string }>(
            null,
            []
        ),
        end_date: new FormControl<Date>(null, []),
    });

    constructor() {
        super();
    }

    public async obterDados(filtros: any) {
        this.loading = true;
        const dados = await apiRhPvfScalesServerShiftsService(filtros);
        this.loading = false;
        return dados;
    }

    protected async obterFiltros() {
        const dataInicio = this.periodo.value?.start_date || undefined;
        const dataFim = this.periodo.value?.end_date || undefined;
        const comarca_id = this.filtros?.value?.comarca_id;
        return {
            ...this.filtros.value,
            comarca_id: comarca_id ? [comarca_id] : undefined,
            lotacao_id: this.filtros.value.lotacao_id,
            cadastrado_por: this.filtros.value.cadastrado_por,
            start_date: formatDate(dataInicio),
            end_date: formatDate(dataFim),
        };
    }

    protected get downloadCsvSincrono() {
        return false;
    }

    limparFiltros() {
        this.filtros.reset();
        this.periodo.reset();
        this.recarregarListagem();
    }
}
