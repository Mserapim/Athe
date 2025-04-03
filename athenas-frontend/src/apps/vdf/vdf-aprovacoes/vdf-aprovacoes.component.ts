import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { VdfAprovacoesService } from './vdf-aprovacoes.service';
import { ApiRhPvfApprovalsRequestsResponseItem } from 'api/rh/api-rh-pvf-approvals-requests.service';
import {
    ApiRhPvfConfigRequestsApproversResponseItem,
    apiRhPvfConfigRequestsApprovers,
} from 'api/rh/api-rh-pvf-config-requests-approvers.service';
import {
    ApiRhPvfConfigRequestsStatusResponseItem,
    apiRhPvfConfigRequestsStatus,
} from 'api/rh/api-rh-pvf-config-requests-status.service';
import {
    ApiRhPvfConfigRequestsTypeResponseItem,
    apiRhPvfConfigRequestsTypes,
} from 'api/rh/api-rh-pvf-config-requests-types.service';
import {
    ApiRhPvfConfigRequestsEmployeeTypesResponseItem,
    apiRhPvfConfigRequestsEmployeeTypes,
} from 'api/rh/api-rh-pvf-config-requests-employee-types.service';
import { ApprovalShowComponent } from '../approval/approval-show/approval-show.component';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'vdf-aprovacoes',
    templateUrl: 'vdf-aprovacoes.component.html',
    standalone: false
})
export class VdfAprovacoesComponent implements OnInit {
    results: ApiRhPvfApprovalsRequestsResponseItem[];
    approvers: ApiRhPvfConfigRequestsApproversResponseItem[];
    statuses: ApiRhPvfConfigRequestsStatusResponseItem[];
    types: ApiRhPvfConfigRequestsTypeResponseItem[];
    employee_types: ApiRhPvfConfigRequestsEmployeeTypesResponseItem[] = [];
    total: number = 0;

    constructor(
        public service: VdfAprovacoesService,
        public dialog: MatDialog,
        private route: ActivatedRoute
    ) {
        const filtros = this.route.snapshot.data?.filtros;

        if (filtros) {
            this.service.filtros.patchValue({
                ...filtros,
            });
        }
    }

    ngOnInit() {
        this.loadApprovers();
        this.loadStatuses();
        this.loadTypes();
        this.loadEmployeeTypes();
        this.configurarColunas();
        this.service.recarregarListagem();
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                titulo: 'Código',
                codigo: 'pk',
                visivel: true,
            },
            {
                titulo: 'Data da solicitação',
                codigo: 'date',
                visivel: true,
                tipo: 'DATA',
            },
            {
                titulo: 'Tipo da solicitação',
                codigo: 'type_of_request',
                visivel: true,
            },
            {
                titulo: 'Solicitante',
                codigo: 'employee_name',
                visivel: true,
            },
            {
                titulo: 'Aprovador atual',
                codigo: 'approver_name',
                visivel: true,
            },
            {
                titulo: 'Situação',
                codigo: 'status_name',
                visivel: true,
            },
            {
                titulo: 'Aguardando aprovador (dias)',
                codigo: 'days_awaiting_approval',
                visivel: true,
            },
            {
                titulo: 'Período aquisitivo',
                codigo: 'acquisitive_period',
                visivel: false,
            },

            {
                codigo: 'visualizar',
                titulo: '',
                visivel: true,
                transformarValor: (linha: any) => {
                    return 'Visualizar';
                },
                tipo: 'LINK',
                acoes: [
                    {
                        icone: 'edit',
                        aoClicar: (linha: any) => this.showDetail2(linha),
                    },
                ],
            },
        ]);
    }
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
            this.service.recarregarListagem();
        });
    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];

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
}
