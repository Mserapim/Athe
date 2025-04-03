import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { VdfPlantoesService } from './vdf-plantoes.service';
import { ApiRhPvfApprovalsRequestsResponseItem } from 'api/rh/api-rh-pvf-approvals-requests.service';
import { ApiRhPvfConfigRequestsApproversResponseItem } from 'api/rh/api-rh-pvf-config-requests-approvers.service';
import {
    ApiRhPvfConfigRequestsStatusResponseItem,
    apiRhPvfConfigRequestsStatus,
} from 'api/rh/api-rh-pvf-config-requests-status.service';
import { ApiRhPvfConfigRequestsTypeResponseItem } from 'api/rh/api-rh-pvf-config-requests-types.service';
import { ApiRhPvfConfigRequestsEmployeeTypesResponseItem } from 'api/rh/api-rh-pvf-config-requests-employee-types.service';
import { ServerShiftNewComponent } from '../server-shift/server-shift-new/server-shift-new.component';
import { ServerShiftEditComponent } from '../server-shift/server-shift-edit/server-shift-edit.component';
import { apiRhPvfConfigServerShiftsPermissionsTypes } from 'api/rh/api-rh-pvf-config-server-shifts-permisions-types.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiRhPvfScalesServerShiftsDeleteService } from 'api/rh/api-rh-pvf-scales-server-shifts.delete';
import { FuseConfirmationDialogComponent } from '@fuse/services/confirmation/dialog/dialog.component';
import { apiRhLocations } from 'api/rh/api-rh-locations.service';
import { MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { apiRhLotacao } from 'api/rh/api-rh-lotacao.service';
import {
    apiRhPvfConfigServerShiftsTypes,
    ApiRhPvfConfigServerShiftsTypesItem,
} from 'api/rh/api-rh-pvf-config-server-shifts-types.service';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Component({
    selector: 'vdf-plantoes',
    templateUrl: 'vdf-plantoes.component.html',
    standalone: false
})
export class VdfPlantoesComponent implements OnInit {
    results: ApiRhPvfApprovalsRequestsResponseItem[];
    approvers: ApiRhPvfConfigRequestsApproversResponseItem[];
    statuses: ApiRhPvfConfigRequestsStatusResponseItem[];
    types: ApiRhPvfConfigRequestsTypeResponseItem[];
    employee_types: ApiRhPvfConfigRequestsEmployeeTypesResponseItem[] = [];
    total: number = 0;
    isOwner: boolean = false;

    constructor(
        protected currentUserService: CurrentUserService,
        public service: VdfPlantoesService,
        public dialog: MatDialog,
        private snackBar: MatSnackBar
    ) {}

    ngOnInit() {
        this.loadTipos();
        this.loadRequestStatus();
        this.currentUserService.load().then(() => {
            this.configurarColunas();
        });

        this.verificarPropriedade();
        this.service.recarregarListagem();
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
    }

    requestStatus: { label: string; value: string }[] = [];
    private async loadRequestStatus() {
        const { results } = await apiRhPvfConfigRequestsStatus({});
        const filteredStatus = results.filter((status) =>
            [2, 3, 4, 10, 5].includes(Number(status.value))
        );
        this.requestStatus = filteredStatus;
    }

    private configurarColunas() {
        const colunas: any = [
            {
                titulo: 'Situação',
                codigo: 'status_name',
                visivel: true,
                ordenavel: true,
            },
            {
                titulo: 'Tipo',
                codigo: 'type_shift_label',
                visivel: true,
                ordenavel: true,
            },
            {
                titulo: 'Plantonista',
                codigo: 'employee_name',
                visivel: true,
                ordenavel: true,
            },
            {
                titulo: 'Comarca',
                codigo: 'comarca',
                visivel: false,
                ordenavel: false,
            },
            {
                titulo: 'Lotação',
                codigo: 'workplace_name',
                visivel: true,
                ordenavel: true,
            },
            {
                titulo: 'Lotação titular',
                codigo: 'lotacao_titular',
                visivel: false,
                ordenavel: true,
            },
            {
                titulo: 'Total em dias',
                codigo: 'days',
                visivel: true,
                ordenavel: true,
            },
            {
                titulo: 'Data início',
                codigo: 'start_date',
                visivel: true,
                ordenavel: true,
                tipo: 'DATA',
            },
            {
                titulo: 'Data fim',
                codigo: 'end_date',
                visivel: true,
                ordenavel: true,
                tipo: 'DATA',
            },
            {
                titulo: 'Criado por',
                codigo: 'criado_por',
                visivel: false,
                ordenavel: true,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Visualizar',
                        icone: 'heroicons_outline:eye',
                        aoClicar: (linha: any) => this.goEdit(linha, true),
                    },
                    {
                        titulo: 'Editar',
                        icone: 'edit',
                        aoClicar: (linha: any) => this.goEdit(linha, false),
                        exibirSe: (linha: any) =>
                            linha.status_name === 'Escala Enviada' &&
                            linha.owner === this.currentUserService.currentUser.id &&
                            this.isOwner,
                    },
                    {
                        titulo: 'Excluir',
                        icone: 'heroicons_outline:trash',
                        aoClicar: (linha: any) => this.excluirItem(linha),
                        exibirSe: (linha: any) =>
                            linha.status_name === 'Escala Enviada' &&
                            linha.owner === this.currentUserService.currentUser.id &&
                            this.isOwner,
                    },
                ],
            },
        ];

        this.service.configurarColunas(colunas);
    }

    public async goNew() {
        let maxHeigth = window.innerWidth <= 768 ? '90%' : '90vh';
        const dialogRef = this.dialog.open(ServerShiftNewComponent, {
            width: '90%',
            maxHeight: '90vh',
            data: {
                close: () => dialogRef.close(),
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.service.recarregarListagem();
        });
    }

    public async goEdit(item, visualizar) {
        const dialogRef = this.dialog.open(ServerShiftEditComponent, {
            width: '90%',
            maxHeight: '90vh',
            data: {
                visualizar: visualizar,
                id: item.pk,
                close: () => dialogRef.close(),
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            this.service.recarregarListagem();
        });
    }

    async excluirItem(linha: any) {
        const dialogData = {
            title: 'Confirmação de exclusão',
            message: 'Tem certeza que deseja excluir este plantão?',
            icon: { name: 'warning', color: 'warn' },
            actions: {
                cancel: {
                    show: true,
                    label: 'Cancelar',
                },
                confirm: {
                    show: true,
                    label: 'Apagar',
                    useStyle: true,
                    style: {
                        backgroundColor: '#dc2626',
                        color: 'white',
                        border: 'none',
                    },
                },
            },
        };

        const dialogRef = this.dialog.open(FuseConfirmationDialogComponent, {
            width: '400px',
            data: dialogData,
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result === 'confirmed') {
                apiRhPvfScalesServerShiftsDeleteService({ id: linha.pk })
                    .then(() => {
                        this.snackBar.open(
                            'Plantão excluído com sucesso!',
                            '',
                            { duration: 3000 }
                        );
                        this.service.recarregarListagem();
                    })
                    .catch((error) => {
                        let errorMessage =
                            error?.response?.data?.detail ||
                            'Erro desconhecido ao excluir o plantão.';
                        console.error('Erro ao excluir o plantão:', error);
                        this.snackBar.open(
                            `Erro ao excluir o plantão: ${errorMessage}`,
                            '',
                            { duration: 5000 }
                        );
                    });
            }
        });
    }

    tipos: ApiRhPvfConfigServerShiftsTypesItem[];
    private async loadTipos() {
        const { results } = await apiRhPvfConfigServerShiftsTypes({});
        this.tipos = results;
    }

    selecaoLotacao: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhLotacao,
        obterTitulo: 'name',
        obterFiltros: (payload) => {
            return {
                per_page: 15,
                page: 1,
                keyword: payload.palavra_chave,
            };
        },
    };

    selecaoComarca: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhLocations,
        obterTitulo: 'name',
        obterValor: 'comarca',
        obterFiltros: (payload) => {
            return {
                estado: 79,
                per_page: 15,
                page: 1,
                keyword: payload.palavra_chave,
            };
        },
    };
}
