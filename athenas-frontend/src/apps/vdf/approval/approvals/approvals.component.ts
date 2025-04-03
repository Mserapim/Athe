import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { useGet } from 'api/@base/use-get';
import { tap } from 'rxjs';
// import { RequestsDataSource } from './approvals.datasource';
import {
    ApprovalsAdvancedFilterDialog,
    RequestsAdvancedFilterDialogData,
} from './approvals-advanced-filter/approvals-advanced-filter-dialog.component';
import { PvfApprovalsDataSource } from 'datasources/pvf-approvals.datasource';
import { RequestShowUsufructComponent } from '../../request/request-show-usufruct/request-show-usufruct.component';
import { requestShowAbsenceComponent } from '../../request/request-show-absence/request-show-absence.component';
import {
    isRequestTypeAbsence,
    isRequestTypeTelework,
    isRequestTypeUsufruct,
} from 'enums/request-type.enum';
import { ApprovalShowUsufructComponent } from '../approval-show-usufruct/approval-show-usufruct.component';
import { apiRhPvfConfigRequestsApprovers } from 'api/rh/api-rh-pvf-config-requests-approvers.service';
import { ApiRhPvfConfigRequestsApproversResponseItem } from 'api/rh/api-rh-pvf-config-requests-approvers.service';
import { apiRhPvfApprovalsRequests } from 'api/rh/api-rh-pvf-approvals-requests.service';
import { ApiRhPvfApprovalsRequestsResponseItem } from 'api/rh/api-rh-pvf-approvals-requests.service';
import {
    ApiRhPvfConfigRequestsStatusResponseItem,
    apiRhPvfConfigRequestsStatus,
} from 'api/rh/api-rh-pvf-config-requests-status.service';
import {
    ApiRhPvfConfigRequestsTypeResponseItem,
    apiRhPvfConfigRequestsTypes,
} from 'api/rh/api-rh-pvf-config-requests-types.service';
import { ApprovalShowTeleworkComponent } from '../approval-show-telework/approval-show-telework.component';
import { RequestShowComponent } from '../../request/components/request-show/request-show.component';
import { ApprovalShowComponent } from '../approval-show/approval-show.component';
import {
    ApiRhPvfConfigRequestsEmployeeTypesResponseItem,
    apiRhPvfConfigRequestsEmployeeTypes,
} from 'api/rh/api-rh-pvf-config-requests-employee-types.service';

@Component({
    selector: 'app-approvals',
    templateUrl: './approvals.component.html',
    styleUrls: ['./approvals.component.scss'],
    standalone: false
})
export class ApprovalsComponent implements OnInit {
    results: ApiRhPvfApprovalsRequestsResponseItem[];
    approvers: ApiRhPvfConfigRequestsApproversResponseItem[];
    statuses: ApiRhPvfConfigRequestsStatusResponseItem[];
    types: ApiRhPvfConfigRequestsTypeResponseItem[];
    employee_types: ApiRhPvfConfigRequestsEmployeeTypesResponseItem[] = [];
    total: number = 0;

    filters = {
        keyword: '',
        approvals: [],
        employe_types: [],
        request_type: [],
        status: [],
        pending_request: true,
    };

    @ViewChild(MatPaginator) paginator: MatPaginator;

    displayedColumns: string[] = [
        'pk',
        'date',
        'type_of_request',
        'employee_name',
        'approver_name',
        'status_name',
        'days_awaiting_approval',
        'action',
    ];

    constructor(public dialog: MatDialog) {}

    public showDetail2(element: any) {
        const { pk: requestId, portal_request_type, status } = element;

        const dialogRef = this.dialog.open(ApprovalShowComponent, {
            width: '98%',
            maxWidth: '98vw',
            maxHeight: '98vh',
            data: {
                requestId,
                close: () => {
                    dialogRef.close;
                    // this.loadPage();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.loadPage();
        });
    }

    async ngOnInit() {
        await this.loadApprovers();
        await this.loadStatuses();
        await this.loadTypes();
        await this.loadEmployeeTypes();
        await this.loadPage();
        this.applyFilter();

        // this.showDetail({
        //     //TODO
        //     pk: 33460,
        // });
    }

    ngAfterViewInit() {
        this.paginator.page.pipe(tap(() => this.loadPage())).subscribe();
    }

    public async loadApprovers() {
        const { results } = await apiRhPvfConfigRequestsApprovers({});
        this.approvers = results;
    }

    public async loadStatuses() {
        const { results } = await apiRhPvfConfigRequestsStatus({});
        this.statuses = results;
    }

    public async loadTypes() {
        const { results } = await apiRhPvfConfigRequestsTypes({});
        this.types = results;
    }

    public async loadEmployeeTypes() {
        const { results } = await apiRhPvfConfigRequestsEmployeeTypes({});
        this.employee_types = results;
    }

    public showDetail(element: any) {
        // const { pk: requestId, portal_request_type } = element;
        // console.log('teste', element);
        this.showDetail2(element);
    }

    public clearKeyword() {
        this.filters.keyword = '';
        this.applyFilter();
    }

    public applyFilter() {
        this.paginator.pageIndex = 0;
        this.loadPage();
    }

    async loadPage() {
        const { results, total } = await apiRhPvfApprovalsRequests({
            ...(this.filters || { keyword: '' }),
            page: (this.paginator?.pageIndex || 0) + 1,
            per_page: this.paginator?.pageSize || 10,
        });
        this.results = results;
        this.total = total;
    }
}
