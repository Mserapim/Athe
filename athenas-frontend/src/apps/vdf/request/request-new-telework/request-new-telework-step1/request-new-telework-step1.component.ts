import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStatusEnum, canRequestCancel } from 'enums/request-status.enum';
import { requestStatusLabel } from 'enums/request-status.enum';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewTeleworkService } from '../request-new-telework.service';
import { apiReportRhPvfPointSheetService } from 'api/report/api-report-rh-pvf-point-sheet';
import { useDownload } from 'api/@base/use-download';
import { apiRhPvfRequestsIdCancelService } from 'api/rh/api-rh-pvf-requests-id-cancel.service';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { MatDialog } from '@angular/material/dialog';
import { textoNormalMobile } from '../../../../../utils/texto-normal-mobile';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FuseConfirmationService } from '@fuse/services/confirmation';

@Component({
    selector: 'request-new-telework-step1',
    templateUrl: 'request-new-telework-step1.component.html',
    styleUrls: ['../../request.component.scss'],
    standalone: false
})
export class RequestNewTeleworkStep1Component {
    currentTab: string = 'DETAIL';
    textoCancelar: string;
    public isLoadingFolhaPonto: boolean = false;

    constructor(
        protected stepper: RequestStepperService,
        protected router: Router,
        public dialog: MatDialog,
        private mpPdfPreviewComponent: MpPdfPreviewComponent,
        protected service: RequestNewTeleworkService,
        private _fuseConfirmationService: FuseConfirmationService,
        protected snackBar: MatSnackBar,
    ) {
        stepper.currentStep = 0;
    }

    async ngOnInit() {
        await this.service.loadTeleworkStatus();

        this.textoCancelar = textoNormalMobile(
            'Deseja cancelar essa solicitação?',
            'Cancelar'
        );
    }

    public requestStatusLabel(requestStatus: RequestStatusEnum) {
        return requestStatusLabel(requestStatus);
    }

    get hasTeleworkPending() {
        return this.service?.teleworkStatus?.telework_pending;
    }

    get countWorkplanActive() {
        return this.service?.teleworkStatus?.send_workplan_reference;
    }

    get isValid() {
        if (!this.hasTeleworkPending) return false;
        if (!this.service.request) return false;
        if (this.service.request.status != RequestStatusEnum.AGUARDANDO_ENVIO)
            return false;
        return true;
    }

    async downloadTimeSheet() {
        this.isLoadingFolhaPonto = true;
        this.service.messageSuccess = '';
        this.service.messageError = '';
        const referenceSplited = this.service.request.reference.split('/');
        const year = +referenceSplited[1];
        const month = +referenceSplited[0];
        const { message, uuid, success } =
            await apiReportRhPvfPointSheetService({
                employee_id: this.service.request.employee,
                month,
                year,
            });

        if (success) this.service.messageSuccess = message;
        else this.service.messageError = message;

        if (!success) return;

        const link = await useDownload(uuid, 0, 30, {
            automaticDownload: false,
        });

        this.mpPdfPreviewComponent.open(link);
        this.isLoadingFolhaPonto = false;
    }

    goNext() {
        this.router.navigate([`vdf/solicitacoes/novo/teletrabalho`, 'step2']);
    }

    get canCancel() {
        return canRequestCancel(this.service.request.status);
    }

    public async cancelRequest() {
        this.service.message = null;
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
                        requestId: this.service.request.pk,
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
