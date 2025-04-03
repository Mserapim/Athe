import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { RhPvfMinhasSolicitacoesDataSource } from 'datasources/rh-pvf-minhas-solicitacoes.datasource';
import { printDate } from 'utils/print-date';
import { MatPaginator } from '@angular/material/paginator';
import { tap } from 'rxjs';

@Component({
    selector: 'app-minhas-substituicoes',
    templateUrl: './minhas-substituicoes.component.html',
    standalone: false
})
export class MinhasSubstituicoesComponent implements OnInit {
    @ViewChild(MatPaginator) paginator: MatPaginator;

    printDate = printDate;

    dataSource = new RhPvfMinhasSolicitacoesDataSource();

    filters: {
        keyword: string | undefined;
        tipo_acao: number | undefined;
        dt_inicio: Date | undefined;
        dt_fim: Date | undefined;
    } = {
        keyword: undefined,
        tipo_acao: undefined,
        dt_inicio: undefined,
        dt_fim: undefined,
    };

    displayedColumns: string[] = [
        'serv_substituto',
        'serv_substituido',
        'data_inicio',
        'data_fim',
        'titularidade',
        'cumulativa',
    ];

    constructor(public dialog: MatDialog) {}

    ngOnInit() {
        this.dataSource.load({
            page: 1,
            per_page: 10,
        });
    }

    applyFilter() {
        this.dataSource.load({
            ...this.filters,
            page: (this.paginator.pageIndex || 0) + 1,
            per_page: this.paginator.pageSize,
            dt_inicio: this.filters?.dt_inicio?.toISOString()?.substring(0, 10),
            dt_fim: this.filters?.dt_fim?.toISOString()?.substring(0, 10),
        });
    }

    ngAfterViewInit() {
        this.paginator.page.pipe(tap(() => this.applyFilter())).subscribe();
    }

    tipoAcoes = [
        { value: undefined, label: 'Todos' },
        { value: 1, label: 'Substitui' },
        { value: 2, label: 'Substituido' },
    ];
}
