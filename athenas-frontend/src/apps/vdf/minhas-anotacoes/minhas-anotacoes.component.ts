import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { printDate } from 'utils/print-date';
import { MatPaginator } from '@angular/material/paginator';
import { tap } from 'rxjs';
import { RhPvfMinhasAnotacoesDataSource } from 'datasources/rh-pvf-minhas-anotacoes.datasource';
import { MinhasAnotacoesShow } from './minhas-anotacoes-show/minhas-anotacoes-show.component';
import { apiReportRhPvfAnotacaoPessoalService } from 'api/report/api-report-rh-pvf-anotacao-pessoal.service';
import { useDownload } from 'api/@base/use-download';
import { apiRhPvfTiposAnotacao } from 'api/rh/api-rh-pvf-tipos-anotacoes.service';
import { Payload } from 'api/report/api-report-rh-pvf-anotacao-pessoal.service';

@Component({
    selector: 'app-minhas-anotacoes',
    templateUrl: './minhas-anotacoes.component.html',
    standalone: false
})
export class MinhasAnotacoesComponent implements OnInit {
    @ViewChild(MatPaginator) paginator: MatPaginator;

    printDate = printDate;

    dataSource = new RhPvfMinhasAnotacoesDataSource();

    tiposAnotacao: { label: string; value: string }[] = [];
    filters: {
        keyword: string | undefined;
        tipo_anotacao_id: number[] | undefined;
    } = { keyword: undefined, tipo_anotacao_id: [] };

    displayedColumns: string[] = [
        'tipo_label',
        'documento_tipo_label',
        'publicacao_label',
        'documento_numero',
        'documento_data',
        'gedoc_numero',
        'anotacao',
    ];

    constructor(public dialog: MatDialog) {}

    ngOnInit() {
        this.loadTiposAnotacao();
        this.load();
    }

    public async load() {
        await this.dataSource.load({
            page: 1,
            per_page: 10,
        });
    }

    private async loadTiposAnotacao() {
        const { results } = await apiRhPvfTiposAnotacao({});
        this.tiposAnotacao = results;
    }

    applyFilter() {
        this.dataSource.load({
            ...this.filters,
            tipo_anotacao_id: this.filters.tipo_anotacao_id.join(','),
            page: (this.paginator.pageIndex || 0) + 1,
            per_page: this.paginator.pageSize,
        });
    }

    ngAfterViewInit() {
        this.paginator.page.pipe(tap(() => this.applyFilter())).subscribe();
    }

    public showAnotacao(element: any) {
        const dialogRef = this.dialog.open(MinhasAnotacoesShow, {
            width: '99%',
            maxHeight: '90vh',
            data: { element },
        });

        dialogRef.afterClosed().subscribe((result) => {});
    }

    isLoading: boolean = false;

    async download() {
        try {
            this.isLoading = true;

            let payload: Payload = {};

            if (
                this.filters.tipo_anotacao_id &&
                this.filters.tipo_anotacao_id.length > 0
            ) {
                payload.tipos_anotacao = this.filters.tipo_anotacao_id;
            }

            const { message, uuid, success } =
                await apiReportRhPvfAnotacaoPessoalService(payload);

            if (!success) return;

            await useDownload(uuid);
        } finally {
            this.isLoading = false;
        }
    }
}
