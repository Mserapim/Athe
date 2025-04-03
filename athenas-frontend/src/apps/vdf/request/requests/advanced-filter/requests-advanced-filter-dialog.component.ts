import { Component, Inject } from '@angular/core';
import { FormControl } from '@angular/forms';
import {
    MatDialog,
    MatDialogRef,
    MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { PvfConfigRequestTypesDataSource } from 'datasources/pvf-config-requests-types.datasource';
import { PvfConfigRequestStatusDataSource } from 'datasources/pvf-config-requests-status.datasource';

export class RequestsAdvancedFilterDialogData {
    keyword: string = '';
    request_type: number[] = [];
    status: number[] = [];
}

@Component({
    selector: 'requests-advanced-filter-dialog',
    templateUrl: 'requests-advanced-filter-dialog.html',
    standalone: false
})
export class RequestsAdvancedFilterDialog {
    requestTypesDataSource: PvfConfigRequestTypesDataSource;
    requestStatusDataSource: PvfConfigRequestStatusDataSource;

    constructor(
        public dialogRef: MatDialogRef<RequestsAdvancedFilterDialog>,
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
