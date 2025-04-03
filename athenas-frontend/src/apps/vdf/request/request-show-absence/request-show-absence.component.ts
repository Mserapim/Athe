import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { ActivatedRoute } from '@angular/router';
import {
    ApiRhPvfRequestsIdResponse,
    apiRhPvfRequestsId,
} from 'api/rh/api-rh-pvf-requests-id.service';
import { BehaviorSubject } from 'rxjs';
import {
    RequestStatusEnum,
    requestStatusLabel,
} from 'enums/request-status.enum';
import { apiRhPvfRequestsIdHistories } from 'api/rh/api-rh-pvf-requests-id-histories.service';
import { RequestTypeEnum } from 'enums/request-type.enum';
import { apiRhPvfRequestsAbsencesHealthLicensesId } from 'api/rh/api-rh-pvf-requests-absences-health-licenses-id.service';
import { apiGedDownload } from 'api/ged/api-ged-download.service';
import { apiRhPvfRequestsAbsencesMourningAbsencesId } from 'api/rh/api-rh-pvf-requests-absences-mourning-absences-id.service';

export class requestShowAbsenceComponentData {
    requestId: number;
}

@Component({
    selector: 'request-show-absence',
    templateUrl: './request-show-absence.component.html',
    styleUrls: ['./request-show-absence.component.scss'],
    standalone: false
})
export class requestShowAbsenceComponent implements OnInit {
    public currentTab: string = 'DETALHES';
    public data: ApiRhPvfRequestsIdResponse = {} as any;
    public detail: any = {};
    public usufructs: any = {};
    public histories: any[] = [];

    constructor(
        private route: ActivatedRoute,
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA) payload: requestShowAbsenceComponentData
    ) {
        this.load(payload);
    }

    ngOnInit() {}

    private async load({ requestId }: { requestId: number }) {
        this.data = await apiRhPvfRequestsId({
            requestId,
        });

        if (
            this.data.portal_request_type ==
            RequestTypeEnum.TRATAMENTO_SAUDE_15_DIAS
        )
            this.detail = await apiRhPvfRequestsAbsencesHealthLicensesId({
                requestId,
            });

        if (this.data.portal_request_type == RequestTypeEnum.FALECIMENTO) {
            this.detail = await apiRhPvfRequestsAbsencesMourningAbsencesId({
                requestId,
            });
        }

        // this.data.portal_request_type == RequestType.

        // const { results: usufructs } = await apiRhPvfRequestsIdUsufructs({
        //     id: requestId,
        // });

        const { results: histories } = await apiRhPvfRequestsIdHistories({
            requestId,
        });
        this.histories = histories;

        // this.usufructs = usufructs;
        // console.log(response);
    }

    public requestStatusLabel(requestStatus: RequestStatusEnum) {
        return requestStatusLabel(requestStatus);
    }

    public async show({ requestId }: { requestId: number }) {
        const dialogRef = this.dialog.open(requestShowAbsenceComponent, {
            width: '90%',
            data: { requestId },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                //this.applyFilter();
            }
        });
    }

    public async download(id) {
        const response = await apiGedDownload({
            file_id: id,
        });

        console.log(response);
    }
}
