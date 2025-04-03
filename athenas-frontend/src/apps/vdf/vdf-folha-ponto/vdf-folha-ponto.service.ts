import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDatepicker } from '@angular/material/datepicker';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiFolhaPontoMarcacoes } from 'api/folha-ponto/api-folha-ponto-marcacoes.service';
import { MpmtListagem2Service } from 'components/mpmt-listagem2/mpmt-listagem2.service';
import { Moment } from 'moment';
import { formatDate } from 'utils/format-date';

@Injectable()
export class VdfFolhaPontoService extends MpmtListagem2Service {
    public periodo = new FormGroup({
        fim: new FormControl<Date | null>(null, []),
        inicio: new FormControl<Date | null>(null, []),
    });

    filtros = new FormGroup({
        fim: new FormControl<number>(null, []),
        inicio: new FormControl<string>(null, []),
        competencia: new FormControl<Moment>(null, []),
        ano: new FormControl<number>(null, []),
        mes: new FormControl<number>(null, []),
        keyword: new FormControl<string>(null, []),
        servidor_id: new FormControl<number>(null, []),
        lotacao_id: new FormControl<number>(null, []),
        tipos_dia: new FormControl<number[]>(null, []),
        tipo_filtro: new FormControl<'COMPETENCIA' | 'PERIODO'>(
            'COMPETENCIA',
            []
        ),
    });

    constructor(protected snackBar: MatSnackBar) {
        super();
    }

    limparFiltros() {
        this.filtros.reset();
        this.periodo.reset();
        this.filtros.patchValue({
            tipo_filtro: 'COMPETENCIA',
        });
    }

    public async obterDados(filtros: any) {
        this.resetar();
        this.startLoading();
        try {
            const { data } = await apiFolhaPontoMarcacoes(filtros);
            return data;
        } catch (e) {
            this.exibirErro(e?.response?.data?.message);
            throw e;
        } finally {
            this.stopLoading();
        }
    }

    protected async obterFiltros() {
        const inicioDate = this.periodo.value?.inicio || undefined;
        const fimDate = this.periodo.value?.fim || undefined;

        const tipoFiltro = this.filtros?.value.tipo_filtro;

        const inicio =
            tipoFiltro == 'PERIODO' ? formatDate(inicioDate) : undefined;
        const fim = tipoFiltro == 'PERIODO' ? formatDate(fimDate) : undefined;

        const competencia =
            tipoFiltro == 'COMPETENCIA'
                ? this.filtros.value.competencia
                : undefined;
        const mes = competencia?.month() + 1 || undefined;
        const ano = competencia?.year() || undefined;

        return {
            ...this.filtros.value,
            competencia: undefined,
            inicio,
            fim,
            mes,
            ano,
        };
    }

    selecionarCompetencia(
        normalizedMonthAndYear: Moment,
        datepicker: MatDatepicker<Moment>
    ) {
        this.filtros.patchValue({
            competencia: normalizedMonthAndYear,
            mes: normalizedMonthAndYear.month(),
            ano: normalizedMonthAndYear.year(),
        });
        datepicker.close();
        this.recarregarListagem();
    }

    selecionarData(
        normalizedMonthAndYear: Moment,
        datepicker: MatDatepicker<Moment>
    ) {
        datepicker.open();
    }

    compentenciaFormatado() {
        if (!this.filtros?.value?.competencia) return '';
        const data = this.filtros?.value?.competencia;
        return `${(data.month() + 1).toString().padStart(2, '0')}/${data
            .year()
            .toString()
            .padStart(2, '0')}`;
    }

    protected get downloadCsvSincrono() {
        return false;
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected exibirErro(e: any) {
        const detalheErro = e || '';
        const texto = `${detalheErro}`;
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }
}
