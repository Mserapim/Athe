import { Component, Inject, Input, OnChanges, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { apiRhPvfRequestsMovementsVerticalProgressionsDocumentsDelete } from 'api/rh/api-rh-pvf-requests-movements-vertical-progressions-documents-id-delete.service';
import { apiRhPvfRequestsMovementsVerticalProgressionsDocuments } from 'api/rh/api-rh-pvf-requests-movements-vertical-progressions-documents-id-put.service';
import { apiRhPvfRequestsMovementsVerticalProgressionsDocumentsPost } from 'api/rh/api-rh-pvf-requests-movements-vertical-progressions-documents-post.service';

export class RequestShowProgressaoVerticalRemoveComponentData {
    requestId: string;
    pk: number;
    description: string;
    close: Function;
}
@Component({
    selector: 'request-show-progressao-vertical-remove',
    templateUrl: './request-show-progressao-vertical-remove.component.html',
    standalone: false
})
export class RequestShowProgressaoVerticalRemoveComponent
    implements OnInit, OnChanges
{
    message: string;
    isLoading: boolean;

    constructor(
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestShowProgressaoVerticalRemoveComponentData
    ) {}

    ngOnInit() {}

    ngOnChanges(changes) {}

    get isValid() {
        return this.payload.pk;
    }

    get description() {
        return this.payload.description;
    }

    async goConfirm() {
        try {
            this.isLoading = true;
            this.message = '';
            await apiRhPvfRequestsMovementsVerticalProgressionsDocumentsDelete({
                id: this.payload.pk,
            });
            this.goBack();
        } catch (e) {
            this.message = e?.response?.data?.message || e;
        } finally {
            this.isLoading = false;
        }
    }

    goBack() {
        this.payload?.close();
    }
}
