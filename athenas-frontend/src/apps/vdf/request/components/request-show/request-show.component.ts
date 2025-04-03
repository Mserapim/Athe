import { Component, Inject, Input, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { apiRhPvfApprovalsRequestsId } from 'api/rh/api-rh-pvf-approvals-requests-id.service';
import {
    ApiRhPvfRequestsIdResponse,
    apiRhPvfRequestsId,
} from 'api/rh/api-rh-pvf-requests-id.service';
import {
    isRequestDesbloqueioTeletrabalho,
    isRequestRelatorioTeletrabalhoSemestral,
    isRequestSolicitacaoCreditoDispensaEleitoral,
    isRequestTipoCancelamentoTeletrabalho,
    isRequestTipoSolicitacaoAuxilioCrecheIr,
    isRequestTipoSolicitacaoCreditoFolga,
    isRequestTypeAbsence,
    isRequestTypeCancel,
    isRequestTypeExecicioCumulativo,
    isRequestTypeProgressaoHorizontal,
    isRequestTypeProgressaoVertical,
    isRequestTypeRetificationUsufruct,
    isRequestTypeShiftServerConfirm,
    isRequestTypeTelework,
    isRequestTypeTimesheet,
    isRequestTypeUsufruct,
} from 'enums/request-type.enum';
import { BehaviorSubject, Subject } from 'rxjs';
import { RequestStatusEnum } from '../../../../../enums/request-status.enum';
import {
    apiVdfSolicitacaoCreditoEleitoralDetalhes
} from "../../../../../api/vdf/api-vdf-solicitacao-credito-dispensa-eleitoral-detalhes.service";

export class RequestShowComponentData {
    requestId: number;
    status: RequestStatusEnum;
    close: () => void;
}

type KEY =
    | 'EXERCICIO_CUMULATIVO'
    | 'USUFRUCTS'
    | 'TIMESHEET_JUSTIFICATIONS'
    | 'TIMESHEET_SOLICITACAO_AFASTAMENTO'
    | 'TIMESHEET_PENDINGS'
    | 'TELEWORK_TARGETS'
    | 'TELEWORK_AFASTAMENTOS'
    | 'HISTORIC'
    | 'SUBSTITUTES'
    | 'RETIFICATIONS'
    | 'ABSENCES'
    | 'HORIZONTAL_PROGRESSIONS'
    | 'PROGRESSAO_VERTICAL'
    | 'SERVER_SHIFT_CONFIRM'
    | 'CANCELAMENTO_TELETRABALHO'
    | 'RELATORIO_TELETRABALHO_SEMESTRAL_SERVIDORES'
    | 'RELATORIO_TELETRABALHO_SEMESTRAL_QUESTIONARIO'
    | 'SOLICITACAO_FOLGA'
    | 'SOLICITACAO_AUX_CRECHE_IR'
    | 'SOLICITACAO_AUX_CRECHE_IR_EDITAR'
    | 'DESBLOQUEAR_TELETRABALHO'
    | 'SOLICITACAO_CREDITO_DISPENSA_ELEITORAL';

class TabItem {
    key: KEY;
    label: string;
}

@Component({
    selector: 'request-show',
    templateUrl: './request-show.component.html',
    styleUrls: ['./request-show.component.scss'],
    standalone: false
})
export class RequestShowComponent implements OnInit {
    public requestId: number;
    public currentTab: KEY = 'USUFRUCTS';
    public request: ApiRhPvfRequestsIdResponse = {};
    public dialogClass = RequestShowComponent;
    public showActions = false;

    private tabsSubject = new BehaviorSubject<TabItem[]>([]);
    public tabs$ = this.tabsSubject.asObservable();

    get serviceDetail() {
        return apiRhPvfRequestsId;
    }

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        private dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestShowComponentData
    ) {
        this.load(payload).then();
    }

    ngOnInit() {}

    protected async load({ requestId }: { requestId: number }) {
        const response = await this.serviceDetail({
            requestId,
        });

        this.request = response;

        this.calculateTabs();
    }

    calculateTabs() {
        if (
            isRequestDesbloqueioTeletrabalho(this.request.portal_request_type)
        ) {
            this.currentTab = 'HISTORIC';
            this.tabsSubject.next([{ key: 'HISTORIC', label: 'Histórico' }]);
        }

        if (
            isRequestRelatorioTeletrabalhoSemestral(
                this.request.portal_request_type
            )
        ) {
            this.currentTab = 'RELATORIO_TELETRABALHO_SEMESTRAL_SERVIDORES';
            this.tabsSubject.next([
                {
                    key: 'RELATORIO_TELETRABALHO_SEMESTRAL_SERVIDORES',
                    label: 'Servidores',
                },
                {
                    key: 'RELATORIO_TELETRABALHO_SEMESTRAL_QUESTIONARIO',
                    label: 'Questionário',
                },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeExecicioCumulativo(this.request.portal_request_type)) {
            this.currentTab = 'EXERCICIO_CUMULATIVO';
            this.tabsSubject.next([
                { key: 'EXERCICIO_CUMULATIVO', label: 'Cumulativo' },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeProgressaoVertical(this.request.portal_request_type)) {
            this.currentTab = 'PROGRESSAO_VERTICAL';
            this.tabsSubject.next([
                { key: 'PROGRESSAO_VERTICAL', label: 'Progressão Vertical' },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (
            isRequestTypeProgressaoHorizontal(this.request.portal_request_type)
        ) {
            this.currentTab = 'HORIZONTAL_PROGRESSIONS';
            this.tabsSubject.next([
                {
                    key: 'HORIZONTAL_PROGRESSIONS',
                    label: 'Progressão Horizontal',
                },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (
            isRequestTypeRetificationUsufruct(this.request.portal_request_type)
        ) {
            this.currentTab = 'RETIFICATIONS';
            this.tabsSubject.next([
                { key: 'RETIFICATIONS', label: 'Retificação' },
                { key: 'SUBSTITUTES', label: 'Substitutos' },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeAbsence(this.request.portal_request_type)) {
            this.currentTab = 'ABSENCES';
            this.tabsSubject.next([
                { key: 'ABSENCES', label: 'Afastamento' },
                { key: 'SUBSTITUTES', label: 'Substitutos' },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeTelework(this.request.portal_request_type)) {
            this.currentTab = 'TELEWORK_TARGETS';
            this.tabsSubject.next([
                { key: 'TELEWORK_TARGETS', label: 'Metas' },
                { key: 'TELEWORK_AFASTAMENTOS', label: 'Afastamentos' },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeUsufruct(this.request.portal_request_type)) {
            this.currentTab = 'USUFRUCTS';
            this.tabsSubject.next([
                { key: 'USUFRUCTS', label: 'Usufrutos' },
                { key: 'SUBSTITUTES', label: 'Substitutos' },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeTimesheet(this.request.portal_request_type)) {
            this.currentTab = 'TIMESHEET_JUSTIFICATIONS';
            this.tabsSubject.next([
                {
                    key: 'TIMESHEET_JUSTIFICATIONS',
                    label: 'Justificativas',
                },
                {
                    key: 'TIMESHEET_SOLICITACAO_AFASTAMENTO',
                    label: 'Sol. Afastamentos',
                },
                { key: 'TIMESHEET_PENDINGS', label: 'Pendências' },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeCancel(this.request.portal_request_type)) {
            this.currentTab = 'USUFRUCTS';
            this.tabsSubject.next([
                {
                    key: 'USUFRUCTS',
                    label: 'Usufrutos',
                },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (
            isRequestTipoCancelamentoTeletrabalho(
                this.request.portal_request_type
            )
        ) {
            this.currentTab = 'CANCELAMENTO_TELETRABALHO';
            this.tabsSubject.next([
                {
                    key: 'CANCELAMENTO_TELETRABALHO',
                    label: 'Teletrabalhos',
                },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (isRequestTypeShiftServerConfirm(this.request.portal_request_type)) {
            this.currentTab = 'SERVER_SHIFT_CONFIRM';
            this.tabsSubject.next([
                {
                    key: 'SERVER_SHIFT_CONFIRM',
                    label: 'Plantões',
                },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (
            isRequestTipoSolicitacaoCreditoFolga(
                this.request.portal_request_type
            )
        ) {
            this.currentTab = 'SOLICITACAO_FOLGA';
            this.tabsSubject.next([
                {
                    key: 'SOLICITACAO_FOLGA',
                    label: 'Solicitação',
                },
                { key: 'HISTORIC', label: 'Histórico' },
            ]);
        }

        if (
            isRequestSolicitacaoCreditoDispensaEleitoral(
                this.request.portal_request_type
            )
        ) {
            if (this.editarCreditoDispensaEleitoral()) {
                this.router.navigate([
                    `vdf/solicitacoes/novo/credito-eleitoral`,
                    'step2', this.payload.requestId
                ]);
                this.close();
            } else {
                this.currentTab = 'SOLICITACAO_CREDITO_DISPENSA_ELEITORAL';
                this.tabsSubject.next([
                    {
                        key: 'SOLICITACAO_CREDITO_DISPENSA_ELEITORAL',
                        label: 'Solicitação',
                    },
                    { key: 'HISTORIC', label: 'Histórico' },
                ]);

                apiVdfSolicitacaoCreditoEleitoralDetalhes({id: this.payload.requestId}).then((response) => {
                    this.request.anexo = response?.anexo
                })
            }
        }

        if (
            isRequestTipoSolicitacaoAuxilioCrecheIr(
                this.request.portal_request_type
            )
        ) {
            if (this.editarAuxilioCreche()) {
                this.currentTab = 'SOLICITACAO_AUX_CRECHE_IR_EDITAR';
                this.tabsSubject.next([
                    {
                        key: 'SOLICITACAO_AUX_CRECHE_IR_EDITAR',
                        label: 'Editar Solicitação',
                    },
                    { key: 'HISTORIC', label: 'Histórico' },
                ]);
            } else {
                this.currentTab = 'SOLICITACAO_AUX_CRECHE_IR';
                this.tabsSubject.next([
                    {
                        key: 'SOLICITACAO_AUX_CRECHE_IR',
                        label: 'Solicitação',
                    },
                    { key: 'HISTORIC', label: 'Histórico' },
                ]);
            }
        }
    }

    close() {
        this.dialog.closeAll();
    }

    editarAuxilioCreche() {
        return this.payload.status == RequestStatusEnum.AGUARDANDO_ENVIO;
    }

    editarCreditoDispensaEleitoral() {
        return this.payload.status == RequestStatusEnum.AGUARDANDO_ENVIO;
    }

    changeRequestFather(request: ApiRhPvfRequestsIdResponse) {
        this.request = request;
    }
}
