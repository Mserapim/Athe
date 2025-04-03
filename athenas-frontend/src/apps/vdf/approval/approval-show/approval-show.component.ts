import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import {
    RequestShowComponent,
    RequestShowComponentData,
} from '../../request/components/request-show/request-show.component';
import { apiRhPvfApprovalsRequestsId } from 'api/rh/api-rh-pvf-approvals-requests-id.service';

@Component({
    selector: 'approval-show',
    templateUrl: '../../request/components/request-show/request-show.component.html',
    styleUrls: [
        '../../request/components/request-show/request-show.component.scss',
    ],
    standalone: false
})
export class ApprovalShowComponent extends RequestShowComponent {
    public showActions: boolean = true;

    get serviceDetail() {
        return apiRhPvfApprovalsRequestsId;
    }

    canCancel = false;

    constructor(
        route: ActivatedRoute,
        protected router: Router,
        dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestShowComponentData
    ) {
        super(route, router, dialog, payload);
    }
}
