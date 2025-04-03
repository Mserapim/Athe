import { Component, Inject, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { useDownload } from 'api/@base/use-download';
import { useGedDownload } from 'api/@base/use-ged-download';
import { apiReportRhPvfPointSheetService } from 'api/report/api-report-rh-pvf-point-sheet';
import { apiReportRhPvfTeleworkService } from 'api/report/api-report-rh-pvf-telework';
import {
    ApiRhPvfRequestsIdResponse,
    apiRhPvfRequestsId,
} from 'api/rh/api-rh-pvf-requests-id.service';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import {
    RequestStatusEnum,
    requestStatusLabel,
} from 'enums/request-status.enum';
import { RequestTypeEnum } from 'enums/request-type.enum';

@Component({
    selector: 'request-show-detail',
    templateUrl: './request-show-detail.component.html',
    styleUrls: ['../../../request.component.scss'],
    standalone: false
})
export class RequestShowDetailComponent implements OnInit {
    @Input() request!: ApiRhPvfRequestsIdResponse;

    displayedColumns = [
        'group',
        'date',
        'employee',
        'action_label',
        'observation',
    ];

    public data: ApiRhPvfRequestsIdResponse = {};

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        private mpPdfPreviewComponent: MpPdfPreviewComponent
    ) {}

    ngOnInit() {
        this.data = this.request;
    }

    protected async load({ requestId }: { requestId: number }) {
        const data = await apiRhPvfRequestsId({
            requestId,
        });
        this.data = data;
    }

    public requestStatusLabel(status: RequestStatusEnum) {
        return requestStatusLabel(this.data?.status);
    }

    get statusGroup() {
        if (
            this.data?.status ==
            RequestStatusEnum.AGUARDANDO_CIENCIA_DO_SUBSTITUTO
        )
            return 'PROGRESS';
        if (this.data?.status == RequestStatusEnum.AGUARDANDO_APROVADOR)
            return 'PROGRESS';
        if (this.data?.status == RequestStatusEnum.AGUARDANDO_EFETIVACAO)
            return 'PROGRESS';
        if (this.data?.status == RequestStatusEnum.EFETIVADO)
            return 'CONFIRMED';
        if (this.data?.status == RequestStatusEnum.INDEFERIDO)
            return 'CANCELED';
        if (this.data?.status == RequestStatusEnum.CANCELADO_DGP)
            return 'CANCELED';
        if (this.data?.status == RequestStatusEnum.CANCELADO_SOLICITANTE)
            return 'CANCELED';
        if (
            this.data?.status ==
            RequestStatusEnum.AGUARDANDO_ASSESSORIA_DA_CORREGEDORIA
        )
            return 'PROGRESS';
        if (this.data?.status == RequestStatusEnum.AGUARDANDO_ENVIO)
            return 'PROGRESS';
        return 'PROGRESS';
    }

    get enableDownloadTimeSheet() {
        return (
            this.data.portal_request_type ==
                RequestTypeEnum.RELATORIO_TELETRABALHO ||
            this.data.portal_request_type == RequestTypeEnum.FOLHA_PONTO
        );
    }

    isLoadingTimeSheet: boolean = false;

    async downloadTimeSheet() {
        try {
            this.isLoadingTimeSheet = true;
            const referenceSplited = this.data.reference.split('/');
            const year = +referenceSplited[1];
            const month = +referenceSplited[0];
            const { message, uuid, success } =
                await apiReportRhPvfPointSheetService({
                    employee_id: this.request.employee,
                    month,
                    year,
                });

            if (!success) return;

            const link = await useDownload(uuid, 0, 30, {
                automaticDownload: false,
            });

            this.mpPdfPreviewComponent.open(link);
        } finally {
            this.isLoadingTimeSheet = false;
        }
    }

    get enableDownloadRelatorioTeletrabalho() {
        return (
            this.data.portal_request_type ==
            RequestTypeEnum.RELATORIO_TELETRABALHO
        );
    }

    isLoadingRelatorioTeletrabalho: boolean = false;

    async downloadRelatorioTeletrabalho() {
        if (this.request && typeof this.request.employee !== 'undefined') {
            try {
                this.isLoadingRelatorioTeletrabalho = true;

                const payload = {
                    plan_work_id: this.request.plan_work_id,
                    send_telework_id: this.request.pk,
                    employee_id: this.request.employee,
                };

                const response = await apiReportRhPvfTeleworkService(payload);

                if (response['uuid']) {
                    await useDownload(response['uuid'].toString());
                }
            } finally {
                this.isLoadingRelatorioTeletrabalho = false;
            }
        }
    }

    async downloadGed() {
        const link = await useGedDownload(this.request.anexo_id.toString());
    }

    async downloadCreditoDispensaEleitoral() {
        const link = await useGedDownload(this.request.anexo.toString());
    }

    enableCreditoDispensaEleitoral() {
        return this.request.anexo != null;
    }
}
