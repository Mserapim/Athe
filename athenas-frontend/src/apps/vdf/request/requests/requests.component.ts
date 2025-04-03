import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { tap } from 'rxjs';
import {
    RequestsAdvancedFilterDialog,
    RequestsAdvancedFilterDialogData,
} from './advanced-filter/requests-advanced-filter-dialog.component';
import { RequestsDataSource } from './requests.datasource';
import {
    RequestTypeEnum,
    isRequestTypeProgressaoHorizontal,
    isRequestTypeTelework,
    isRequestTypeTimesheet, isRequestTipoSolicitacaoAuxilioCrecheIr,
} from 'enums/request-type.enum';
import { Router } from '@angular/router';
import { RequestNewMenuComponent } from '../request-new-menu/request-new-menu.component';
import { apiRhPvfConfigRequestsStatus } from 'api/rh/api-rh-pvf-config-requests-status.service';
import { RequestShowComponent } from '../components/request-show/request-show.component';
import { apiRhPvfConfigRequestsTypes } from 'api/rh/api-rh-pvf-config-requests-types.service';
import { RequestStatusEnum } from 'enums/request-status.enum';
import {
    RequestSolicitacaoAuxilioCrecheIrEditarComponent
} from "../components/request-show/request-show-solicitacao-auxilio-creche-ir/request-solicitacao-auxilio-creche-ir-editar/request-solicitacao-auxilio-creche-ir-editar.component";

@Component({
    selector: 'app-requests',
    templateUrl: './requests.component.html',
    standalone: false
})
export class RequestsComponent implements OnInit {
    @ViewChild(MatPaginator) paginator: MatPaginator;

    filter: any = {};
    requestStatus: { label: string; value: string }[] = [];
    requestTypes: { label: string; value: string }[] = [];

    displayedColumns: string[] = [
        'pk',
        'date',
        'type_of_request',
        'approver_name',
        'status_name',
        'action',
    ];

    dataSource: RequestsDataSource;

    advancedFilterData: RequestsAdvancedFilterDialogData =
        new RequestsAdvancedFilterDialogData();

    constructor(
        private router: Router,
        public dialog: MatDialog // private requestShowComponent: RequestShowComponent, // private requestShowUsufructComponent: RequestShowUsufructComponent, // private requestShowAbsenceComponent: requestShowAbsenceComponent, // private requestShowTeleworkComponent: RequestShowTeleworkComponent
    ) {}

    ngOnInit() {
        this.dataSource = new RequestsDataSource();

        this.load();
    }

    goLink(link: string) {
        this.router.navigate([link]);
    }

    ngAfterViewInit() {
        this.paginator.page.pipe(tap(() => this.loadPage())).subscribe();
    }

    actionView(element: {
        status: RequestStatusEnum;
        portal_request_type: RequestTypeEnum;
    }) {
        if (this.actionContinue(element)) return false;
        return true;
    }

    actionContinue(element: {
        status: RequestStatusEnum;
        portal_request_type: RequestTypeEnum;
    }) {
        if (isRequestTypeProgressaoHorizontal(element.portal_request_type))
            if (element.status == 9)
                //AGUARDANDO_ENVIO
                return true;
        if (isRequestTypeTelework(element.portal_request_type))
            if (element.status == 9)
                //AGUARDANDO_ENVIO
                return true;
        if (isRequestTypeTimesheet(element.portal_request_type))
            if (element.status == 9)
                //AGUARDANDO_ENVIO
                return true;
        if (isRequestTipoSolicitacaoAuxilioCrecheIr(element.portal_request_type))
            if (element.status == 9)
                //AGUARDANDO_ENVIO
                return true;
        return false;
    }

    goContinue(element: {
        status: RequestStatusEnum;
        portal_request_type: RequestTypeEnum;
    }) {
        if (isRequestTypeTelework(element.portal_request_type)) {
            this.router.navigate(['/vdf/solicitacoes/novo/teletrabalho/step1']);
        }
        if (isRequestTypeTimesheet(element.portal_request_type)) {
            this.router.navigate(['/vdf/solicitacoes/novo/folhaponto/step1']);
        }
        if (isRequestTypeProgressaoHorizontal(element.portal_request_type)) {
            this.showDetail(element);
        }
        if (isRequestTipoSolicitacaoAuxilioCrecheIr(element.portal_request_type)){
            this.showDetail(element);
        }
    }

    public async load() {
        await this.dataSource.load({
            page: 1,
            per_page: 10,
        });
        await this.loadRequestStatus();
        await this.loadRequestTypes();
    }

    private async loadRequestStatus() {
        const { results } = await apiRhPvfConfigRequestsStatus({});
        this.requestStatus = results;
    }

    private async loadRequestTypes() {
        const { results } = await apiRhPvfConfigRequestsTypes({});
        this.requestTypes = results;
    }

    public clearKeyword() {
        this.advancedFilterData.keyword = '';
        this.applyFilter();
    }

    public applyFilter() {
        this.paginator.pageIndex = 0;
        this.loadPage();
    }

    public showDetail(element: any) {
        const { pk: requestId, portal_request_type, status } = element;

        const dialogRef = this.dialog.open(RequestShowComponent, {
            width: '98%',
            maxWidth: '98vw',
            maxHeight: '98vh',
            data: {
                requestId,
                status,
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.applyFilter();
            if (result) {
            }
        });
    }

    public showEditAuxilioCrecheIR(element: any) {
        const { pk: requestId, portal_request_type, status } = element;

        const dialogRef = this.dialog.open(RequestSolicitacaoAuxilioCrecheIrEditarComponent, {
            width: '98%',
            maxWidth: '98vw',
            maxHeight: '98vh',
            data: {
                requestId,
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.applyFilter();
            if (result) {
            }
        });
    }

    public openAdvancedFilter(): void {
        const dialogRef = this.dialog.open(RequestsAdvancedFilterDialog, {
            width: '90%',
            data: this.advancedFilterData,
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                this.applyFilter();
            }
        });
    }

    public openMenu() {
        let hasPendingTeleworkRequest = false;
        const requests = this.dataSource.getCurrentRequests();

        hasPendingTeleworkRequest = requests.some(
            (request) =>
                (request.portal_request_type ===
                    RequestTypeEnum.RELATORIO_TELETRABALHO &&
                    request.status ===
                        RequestStatusEnum.AGUARDANDO_APROVADOR) ||
                (request.portal_request_type ===
                    RequestTypeEnum.CANCELAMENTO_TELETRABALHO &&
                    request.status === RequestStatusEnum.AGUARDANDO_APROVADOR)
        );

        const dialogRef = this.dialog.open(RequestNewMenuComponent, {
            width: '90%',
            height: '80%',
            data: {
                hasPendingTeleworkRequest: hasPendingTeleworkRequest,
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                this.applyFilter();
            }
        });
    }

    loadPage() {
        this.dataSource.load({
            keyword: this.advancedFilterData.keyword,
            request_type: this.filter.request_type,
            status: this.filter.status,
            page: (this.paginator.pageIndex || 0) + 1,
            per_page: this.paginator.pageSize,
        });
    }
}
