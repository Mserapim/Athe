import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { VdfSolicitacoesService } from './vdf-solicitacoes.service';
import { apiRhPvfConfigRequestsStatus } from 'api/rh/api-rh-pvf-config-requests-status.service';
import { apiRhPvfConfigRequestsTypes } from 'api/rh/api-rh-pvf-config-requests-types.service';
import { ServerShiftNewComponent } from '../server-shift/server-shift-new/server-shift-new.component';
import { ServerShiftEditComponent } from '../server-shift/server-shift-edit/server-shift-edit.component';
import { RequestShowComponent } from '../request/components/request-show/request-show.component';
import { RequestStatusEnum } from 'enums/request-status.enum';
import {
    RequestTypeEnum,
    isRequestTipoSolicitacaoAuxilioCrecheIr,
    isRequestTypeProgressaoHorizontal,
    isRequestTypeTelework,
    isRequestTypeTimesheet,
} from 'enums/request-type.enum';
import { Router } from '@angular/router';
import { RequestNewMenuComponent } from '../request/request-new-menu/request-new-menu.component';
import { firstValueFrom } from 'rxjs';

@Component({
    selector: 'vdf-solicitacoes',
    templateUrl: 'vdf-solicitacoes.component.html',
    standalone: false
})
export class VdfSolicitacoesComponent implements OnInit {
    requestStatus: { label: string; value: string }[] = [];
    requestTypes: { label: string; value: string }[] = [];

    constructor(
        private router: Router,
        public service: VdfSolicitacoesService,
        public dialog: MatDialog
    ) {}

    ngOnInit() {
        this.loadRequestStatus();
        this.loadRequestTypes();
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    public async openMenu() {
        let hasPendingTeleworkRequest = false;

        const requests = await firstValueFrom(this.service.listagem$);

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
                this.service.recarregarListagem();
            }
        });
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                titulo: 'Código',
                codigo: 'pk',
                visivel: true,
                ordenavel: false,
            },
            {
                titulo: 'Data da solicitação',
                codigo: 'date',
                visivel: true,
                ordenavel: false,
                tipo: 'DATA',
            },
            {
                titulo: 'Tipo da solicitação',
                codigo: 'type_of_request',
                visivel: true,
                ordenavel: false,
            },
            {
                titulo: 'Aprovador atual',
                codigo: 'approver_name',
                visivel: true,
                ordenavel: false,
            },
            {
                titulo: 'Situação',
                codigo: 'status_name',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: '#',
                visivel: true,
                tipo: 'LINK',
                transformarValor: (linha: any) => {
                    if (this.actionContinue(linha)) return 'Editar';
                    if (this.actionView(linha)) return 'Visualizar';
                    return;
                },
                acoes: [
                    {
                        icone: 'edit',
                        aoClicar: (linha: any) => this.goContinue(linha),
                    },
                ],
            },
        ]);
    }

    goContinue(element: {
        status: RequestStatusEnum;
        portal_request_type: RequestTypeEnum;
    }) {
        if (this.actionView(element)) {
            this.showDetail(element);
        }

        if (this.actionContinue(element)) {
            if (isRequestTypeTelework(element.portal_request_type)) {
                this.router.navigate([
                    '/vdf/solicitacoes/novo/teletrabalho/step1',
                ]);
            }
            if (isRequestTypeTimesheet(element.portal_request_type)) {
                this.router.navigate([
                    '/vdf/solicitacoes/novo/folhaponto/step1',
                ]);
            }

            if (
                isRequestTypeProgressaoHorizontal(element.portal_request_type)
            ) {
                this.showDetail(element);
            }

            if (
                isRequestTipoSolicitacaoAuxilioCrecheIr(
                    element.portal_request_type
                )
            ) {
                this.showDetail(element);
            }
        }
    }

    actionView(element: {
        status: RequestStatusEnum;
        portal_request_type: RequestTypeEnum;
    }) {
        return !this.actionContinue(element);
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
        if (
            isRequestTipoSolicitacaoAuxilioCrecheIr(element.portal_request_type)
        )
            if (element.status == 9)
                //AGUARDANDO_ENVIO
                return true;
        return false;
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
            this.service.recarregarListagem();
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
            this.service.recarregarListagem();
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
            this.service.recarregarListagem();
        });
    }

    private async loadRequestStatus() {
        const { results } = await apiRhPvfConfigRequestsStatus({});
        this.requestStatus = results;
    }

    private async loadRequestTypes() {
        const { results } = await apiRhPvfConfigRequestsTypes({});
        this.requestTypes = results;
    }
}
