import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewTimesheetStepperService } from '../request-new-timesheet-stepper/request-new-timesheet-stepper.service';
import { apiRhPvfRequestsSendingTeleworksService } from 'api/rh/api-rh-pvf-requests-sending-teleworks.service';
import { apiRhPvfRequestsId } from 'api/rh/api-rh-pvf-requests-id.service';
import { RequestStatusEnum, canRequestCancel } from 'enums/request-status.enum';
import { requestStatusLabel } from 'enums/request-status.enum';
import { apiRhPvfConfigRequestsTimesheetsReferences } from 'api/rh/api-rh-pvf-config-requests-timesheets-references.service';
import { apiRhPvfConfigEmployeesTimesheetStatus } from 'api/rh/api-rh-pvf-config-employees-timesheet-status.service';
import { apiRhPvfRequestsSendingTimesheetsService } from 'api/rh/api-rh-pvf-requests-sending-timesheets.service';
import { apiReportRhPvfPointSheetService } from 'api/report/api-report-rh-pvf-point-sheet';
import { useDownload } from 'api/@base/use-download';
import { apiRhPvfRequestsIdCancelService } from 'api/rh/api-rh-pvf-requests-id-cancel.service';
import { RequestNewTimesheetService } from '../request-new-timesheet.service';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { textoNormalMobile } from '../../../../../utils/texto-normal-mobile';
import {
    apiRhPvfRequestsIdHistories,
    ApiRhPvfRequestsIdHistoriesResponseItem,
} from 'api/rh/api-rh-pvf-requests-id-histories.service';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
    selector: 'request-new-timesheet-step1',
    templateUrl: 'request-new-timesheet-step1.component.html',
    styleUrls: ['../../request.component.scss'],
    standalone: false
})
export class RequestNewTimesheetStep1Component {
    public title = 'Resumo da solicitação';
    public subtitle = '';

    public request: any = {};
    public usufructs: any = {};
    public histories: any[] = [];
    public references: any[] = [];
    public actions: any[] = [];
    public message: string = null;
    public messageError: string = null;
    public messageSuccess: string = null;
    public selectedReference: string = null;
    public isLoading: boolean = false;
    public isLoadingFolhaPonto: boolean = false;
    public currentTab: string = 'DETAIL';

    textoCancelar: string;

    constructor(
        stepper: RequestNewTimesheetStepperService,
        private service: RequestNewTimesheetService,
        private mpPdfPreviewComponent: MpPdfPreviewComponent,
        private router: Router,
        private _fuseConfirmationService: FuseConfirmationService,
        protected snackBar: MatSnackBar,
    ) {
        stepper.currentStep = 1;
    }

    async ngOnInit() {
        this.findCurrentRequest();
        this.textoCancelar = textoNormalMobile(
            'Deseja cancelar essa solicitação?',
            'Cancelar'
        );
    }

    verifyExists() {
        apiRhPvfRequestsSendingTeleworksService;
    }

    protected async load({ requestId }: { requestId: number }) {
        const response = await apiRhPvfRequestsId({
            requestId,
        });
        this.request = response;
    }

    public async loadReferences() {
        const { results } = await apiRhPvfConfigRequestsTimesheetsReferences(
            {}
        );
        this.references = results;
    }

    public requestStatusLabel(requestStatus: RequestStatusEnum) {
        return requestStatusLabel(requestStatus);
    }

    async findCurrentRequest() {
        try {
            this.isLoading = true;
            const { timesheet_id, active_workplan, timesheet_pending } =
                await apiRhPvfConfigEmployeesTimesheetStatus({
                    page: 1,
                });

            this.service.requestId = timesheet_id;

            if (timesheet_pending)
                if (timesheet_id > 0) {
                    this.load({ requestId: timesheet_id });
                    return;
                }

            await this.loadReferences();

            if (!active_workplan || this.references.length <= 0) {
                await this.createRequest();
                this.findCurrentRequest();
            }
        } finally {
            this.isLoading = false;
        }
    }

    async createRequest() {
        this.messageError = '';
        try {
            const response = await apiRhPvfRequestsSendingTimesheetsService({
                reference: this.selectedReference,
            });
            console.log(response);
        } catch (e) {
            this.messageError =
                e?.response?.data?.message ||
                'Erro inesperado ao criar solicitação';
            throw e;
        }
    }

    get hasRequest() {
        return Object.keys(this.request).length > 0;
    }

    get isValid() {
        return this.hasRequest || this.selectedReference != null;
    }

    async downloadTimeSheet() {
        this.isLoadingFolhaPonto = true;
        this.messageSuccess = '';
        this.message = '';
        const referenceSplited = this.request.reference.split('/');
        const year = +referenceSplited[1];
        const month = +referenceSplited[0];
        const { message, uuid, success } =
            await apiReportRhPvfPointSheetService({
                employee_id: this.request.employee,
                month,
                year,
            });

        if (success) this.messageSuccess = message;
        else this.message = message;

        if (!success) return;

        const link = await useDownload(uuid, 0, 30, {
            automaticDownload: false,
        });

        this.mpPdfPreviewComponent.open(link);
        this.isLoadingFolhaPonto = false;
    }

    async goNext() {
        if (this.hasRequest) {
            return this.router.navigate([
                `vdf/solicitacoes/novo/folhaponto`,
                'step2',
            ]);
        } else {
            if (this.references.length > 0 && this.selectedReference != null) {
                await this.createRequest();
            }

            return this.router.navigate([
                `vdf/solicitacoes/novo/folhaponto`,
                'step2',
            ]);
        }
    }

    get canCancel() {
        return canRequestCancel(this.request.status);
    }

    get canSelectReference() {
        return this.references.length >= 0;
    }

    public async cancelRequest() {
        this.message = null;
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Tem certeza de que deseja cancelar esta solicitação? Essa ação não poderá ser desfeita.',
            icon: {
              show: true,
              name: 'heroicons_outline:exclamation',
              color: 'warn'
            },
            actions: {
                confirm: {
                  show: true,
                  label: 'Executar',
                  style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                  show: true,
                  label: 'Cancelar',
                  style: { 'background-color': '#cbd5e1' },
                }
            },
            dismissible: true
        });

        dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                try {
                    
                    await apiRhPvfRequestsIdCancelService({
                        requestId: this.request.pk,
                    });
                    this.goRequests();
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
        });
    }

    protected exibirMensagem(
        titulo: string,
        texto: string,
        classe: string = 'custom-snackbar'
    ) {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }
}
