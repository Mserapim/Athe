import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { tap } from 'rxjs';
import { PvfServerShiftsDataSource } from 'datasources/pvf-server-shifts.datasource';
import { ServerShiftNewComponent } from '../server-shift-new/server-shift-new.component';
import { ServerShiftEditComponent } from '../server-shift-edit/server-shift-edit.component';
import { apiRhPvfScalesServerShiftsDeleteService } from 'api/rh/api-rh-pvf-scales-server-shifts.delete';
import { apiRhPvfConfigRequestsStatus } from 'api/rh/api-rh-pvf-config-requests-status.service';
import {
    AuthCurrentUserResponse,
    apiAuthCurrentUserService,
} from 'api/auth/api-auth-current-user.service';
import { apiRhPvfConfigServerShiftsPermissionsTypes } from 'api/rh/api-rh-pvf-config-server-shifts-permisions-types.service';

@Component({
    selector: 'app-server-shifts',
    templateUrl: './server-shifts.component.html',
    styleUrls: ['./server-shifts.component.scss'],
    standalone: false
})
export class ServerShiftsComponent implements OnInit {
    @ViewChild(MatPaginator) paginator: MatPaginator;

    filter = {
        keyword: '',
        status: [],
        startDate: null,
        endDate: null,
    };

    requestStatus: { label: string; value: string }[] = [];
    displayedColumns: string[] = [
        'status_name',
        'type_shift_label',
        'employee_name',
        'workplace_name',
        'days',
        'start_date',
        'end_date',
    ];

    dataSource: PvfServerShiftsDataSource;
    currentUser: AuthCurrentUserResponse;
    currentUserId: number;
    minEndDate: Date | null = null;
    isOwner: boolean = false;

    constructor(public dialog: MatDialog) {}

    ngOnInit() {
        this.loadCurrentUser();
        this.verificarPropriedade();
        this.dataSource = new PvfServerShiftsDataSource();
        this.loadRequestStatus();
        this.load();
    }

    ngAfterViewInit() {
        this.paginator.page.pipe(tap(() => this.loadPage())).subscribe();
    }

    public load() {
        this.dataSource.load({
            page: 1,
            per_page: 10,
        });
    }

    private async loadRequestStatus() {
        const { results } = await apiRhPvfConfigRequestsStatus({});
        const filteredStatus = results.filter((status) =>
            [2, 3, 4, 10, 5].includes(Number(status.value))
        );
        this.requestStatus = filteredStatus;
    }

    async loadCurrentUser() {
        try {
            this.currentUser = await apiAuthCurrentUserService({});
            this.currentUserId = this.currentUser.id;
        } catch (error) {
            console.error('Erro ao obter informações do usuário atual', error);
        }
    }

    async verificarPropriedade() {
        try {
            const response = await apiRhPvfConfigServerShiftsPermissionsTypes(
                {}
            );
            if (response && response.results && response.results.length > 0) {
                this.isOwner = true;
            }
        } catch (error) {
            console.error('Erro ao verificar a propriedade', error);
        }
        this.updateColunasExibidas();
    }

    updateColunasExibidas() {
        if (this.isOwner) {
            this.displayedColumns = [
                ...this.displayedColumns,
                'action',
                'delete',
            ];
        } else {
            this.displayedColumns = this.displayedColumns.filter(
                (col) => col !== 'action' && col !== 'delete'
            );
        }
    }

    public clearKeyword() {
        this.filter.keyword = '';
        this.applyFilter();
    }

    public applyFilter() {
        this.paginator.pageIndex = 0;
        this.loadPage();
    }

    loadPage() {
        this.dataSource.load({
            keyword: this.filter.keyword,
            status: this.filter.status,
            startDate: this.filter.startDate
                ? this.filter.startDate.toISOString().split('T')[0]
                : null,
            endDate: this.filter.endDate
                ? this.filter.endDate.toISOString().split('T')[0]
                : null,
            page: (this.paginator.pageIndex || 0) + 1,
            per_page: this.paginator.pageSize,
        });
    }

    public async goNew() {
        const dialogRef = this.dialog.open(ServerShiftNewComponent, {
            width: '90%',
            data: {
                close: () => dialogRef.close(),
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.loadPage();
        });
    }

    public async goEdit(item) {
        const dialogRef = this.dialog.open(ServerShiftEditComponent, {
            width: '90%',
            data: {
                id: item.pk,
                close: () => dialogRef.close(),
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.loadPage();
        });
    }

    async deleteItem(row: any) {
        try {
            await apiRhPvfScalesServerShiftsDeleteService({
                id: row.pk,
            });
            this.load();
        } catch (e) {
            console.error(e);
        }
    }

    onStartDateChange() {
        this.minEndDate = this.filter.startDate;
        this.applyFilter();
    }

    public clearAllFilters() {
        this.filter = {
            keyword: '',
            status: [],
            startDate: null,
            endDate: null,
        };
        this.minEndDate = null;
        this.applyFilter();
    }
}
