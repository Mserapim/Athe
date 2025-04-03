import { Component, Inject } from '@angular/core';
import { FormControl } from '@angular/forms';
import {
    MatDialog,
    MatDialogRef,
    MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { useGet } from 'api/@base/use-get';
import { BehaviorSubject } from 'rxjs';
import { pvfRequestsStatus } from 'services/pvf/requests-status.service';
import { pvfRequestsTypesService } from 'services/pvf/requests-types.service';
import { PvfEventTypesDataSource } from 'datasources/pvf-event-types.datasource';
import { PvfConfigRequestTypesDataSource } from 'datasources/pvf-config-requests-types.datasource';
import { PvfConfigRequestStatusDataSource } from 'datasources/pvf-config-requests-status.datasource';
import { PvfConfigRequestsTypesItem } from 'services/pvf-config-requests-types.service';
import { PvfConfigRequestsStatusItem } from 'services/pvf-config-requests-status.service';

export class RequestsAdvancedFilterDialogData {
    keyword: string = '';
    request_type: number[] = [];
    status: number[] = [];
}

@Component({
    selector: 'approvals-advanced-filter-dialog',
    templateUrl: 'approvals-advanced-filter-dialog.html',
    standalone: false
})
export class ApprovalsAdvancedFilterDialog {
    requestTypesDataSource: PvfConfigRequestTypesDataSource;

    requestStatusDataSource: PvfConfigRequestStatusDataSource;

    constructor(
        public dialogRef: MatDialogRef<ApprovalsAdvancedFilterDialog>,
        @Inject(MAT_DIALOG_DATA) public data: RequestsAdvancedFilterDialogData
    ) {}

    ngOnInit() {
        this.requestTypesDataSource = new PvfConfigRequestTypesDataSource();
        this.requestStatusDataSource = new PvfConfigRequestStatusDataSource();
        this.loadRequestTypes().then();
        this.loadRequestStatus().then();
    }

    async loadRequestTypes() {
        this.requestTypesDataSource.load({
            page: 1,
            per_page: 10,
            year: 2022,
            month: 1,
        });
    }

    async loadRequestStatus() {
        this.requestStatusDataSource.load({
            page: 1,
            per_page: 10,
            year: 2022,
            month: 1,
        });
    }
}
