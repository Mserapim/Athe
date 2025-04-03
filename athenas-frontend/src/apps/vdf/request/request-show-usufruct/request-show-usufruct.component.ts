import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import {
    MAT_DIALOG_DATA,
    MatDialog,
    MatDialogRef,
} from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { apiRhPvfRequestsId } from 'api/rh/api-rh-pvf-requests-id.service';
import { BehaviorSubject } from 'rxjs';
import {
    RequestStatusEnum,
    canRequestCancel,
    requestStatusLabel,
} from 'enums/request-status.enum';
import { apiRhPvfRequestsIdUsufructs } from 'api/rh/api-rh-pvf-requests-id-usufructs.service';
import { apiRhPvfRequestsIdHistories } from 'api/rh/api-rh-pvf-requests-id-histories.service';
import { apiRhPvfApprovalsRequestsIdActions } from 'api/rh/api-rh-pvf-approvals-requests-id-actions.service';
import { apiRhPvfApprovalsRequestsIdAuthorize } from 'api/rh/api-rh-pvf-approvals-requests-id-authorize.service';
import { apiRhPvfRequestsIdCancelService } from 'api/rh/api-rh-pvf-requests-id-cancel.service';
import {textoNormalMobile} from "../../../../utils/texto-normal-mobile";
import { MatSnackBar } from '@angular/material/snack-bar';
import { FuseConfirmationService } from '@fuse/services/confirmation';

export class RequestShowUsufructComponentData {
    requestId: number;
    close: () => void;
}
@Component({
    selector: 'request-show-usufruct',
    templateUrl: './request-show-usufruct.component.html',
    styleUrls: ['./request-show-usufruct.component.scss'],
    standalone: false
})
export class RequestShowUsufructComponent implements OnInit {
    usufructDisplayedColumns = ['start_date', 'end_date', 'days'];
    historiesDisplayedColumns = [
        'group',
        'date',
        'employee',
        'action_label',
        'observation',
    ];

    protected showActions = false;
    protected dialogClass = RequestShowUsufructComponent;
    textoCancelar: string;

    get serviceDetail() {
        return apiRhPvfRequestsId;
    }

    public observation = new FormControl('');

    public currentTab: string = 'USUFRUTOS';
    public data: any = {};
    public usufructs: any = {};
    public histories: any[] = [];
    public actions: any[] = [];
    public message: string = null;

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestShowUsufructComponentData,
        private _fuseConfirmationService: FuseConfirmationService,
        protected snackBar: MatSnackBar,
    ) {
        this.load(payload);
    }

    ngOnInit() {
        this.textoCancelar = textoNormalMobile("Deseja cancelar essa solicitação?", "Cancelar");
    }

    get canCancel() {
        return canRequestCancel(this.data?.status);
    }

    protected async load({ requestId }: { requestId: number }) {
        const response = await this.serviceDetail({
            requestId,
        });

        const { results: usufructs } = await apiRhPvfRequestsIdUsufructs({
            requestId,
        });

        const { results: histories } = await apiRhPvfRequestsIdHistories({
            requestId,
        });

        const { results: actions } = await apiRhPvfApprovalsRequestsIdActions({
            requestId,
        });

        this.data = response;
        this.usufructs = usufructs;
        this.histories = histories;
        this.actions = actions;

        // console.log(actions);
    }

    public requestStatusLabel(status: RequestStatusEnum) {
        return requestStatusLabel(this.data?.status);
    }

    public async show({ requestId }: { requestId: number }) {
        const dialogRef = this.dialog.open(this.dialogClass, {
            width: '90%',
            data: {
                requestId,
                close: () => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                //this.applyFilter();
            }
        });
    }

    public async confirm(action: string) {
        this.message = null;
        try {
            await apiRhPvfApprovalsRequestsIdAuthorize({
                action,
                requestId: this.payload.requestId,
                observation: this.observation.value || '',
                publication: null,
            });
            this.payload.close();
        } catch (e) {
            console.log(e);
            // alert(e?.response?.data?.message);
            this.message = e?.response?.data?.message;
        }
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
                        requestId: this.payload.requestId,
                    });
                    this.payload.close();
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
}
