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
import { apiRhPvfRequestsIdTeleworksTargets } from 'api/rh/api-rh-pvf-requests-id-teleworks-targets.service';
import { textoNormalMobile } from "../../../../utils/texto-normal-mobile";

export class RequestShowTeleworkComponentData {
    requestId: number;
    close: () => void;
}
@Component({
    selector: 'request-show-telework',
    templateUrl: './request-show-telework.component.html',
    standalone: false
})
export class RequestShowTeleworkComponent implements OnInit {
    protected showActions = false;
    protected dialogClass = RequestShowTeleworkComponent;
    textoCancelar: string;

    get serviceDetail() {
        return apiRhPvfRequestsId;
    }

    public observation = new FormControl('');

    public currentTab: string = 'METAS';
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
        public payload: RequestShowTeleworkComponentData
    ) {
        this.load(payload);
    }

    ngOnInit() {
        this.textoCancelar = textoNormalMobile("Deseja cancelar essa solicitação?", "Cancelar");
    }

    get canCancel() {
        return canRequestCancel(this.data.status);
    }

    protected async load({ requestId }: { requestId: number }) {
        const response = await this.serviceDetail({
            requestId,
        });

        const { results: usufructs } = await apiRhPvfRequestsIdTeleworksTargets(
            {
                requestId,
            }
        );

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

    public requestStatusLabel(requestStatus: RequestStatusEnum) {
        return requestStatusLabel(requestStatus);
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
        try {
            await apiRhPvfRequestsIdCancelService({
                requestId: this.payload.requestId,
            });
            this.payload.close();
        } catch (e) {
            console.log(e);
            // alert(e?.response?.data?.message);
            this.message = e?.response?.data?.message;
        }
    }
}
