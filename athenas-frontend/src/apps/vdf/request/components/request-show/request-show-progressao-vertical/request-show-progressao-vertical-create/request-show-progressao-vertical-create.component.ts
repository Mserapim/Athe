import { Component, Inject, Input, OnChanges, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { apiRhPvfRequestsMovementsVerticalProgressionsDocuments } from 'api/rh/api-rh-pvf-requests-movements-vertical-progressions-documents-id-put.service';
import { apiRhPvfRequestsMovementsVerticalProgressionsDocumentsPost } from 'api/rh/api-rh-pvf-requests-movements-vertical-progressions-documents-post.service';

export class RequestShowProgressaoVerticalCreateComponentData {
    requestId: string;
    close: Function;
}
@Component({
    selector: 'request-show-progressao-vertical-create',
    templateUrl: './request-show-progressao-vertical-create.component.html',
    standalone: false
})
export class RequestShowProgressaoVerticalCreateComponent
    implements OnInit, OnChanges
{
    @Input() requestId!: number;
    file: any;
    attachmentId: any;
    name: string;
    message: string;
    isLoading: boolean;

    constructor(
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestShowProgressaoVerticalCreateComponentData,
        private dialogRef: MatDialogRef<RequestShowProgressaoVerticalCreateComponent>,
    ) {}

    ngOnInit() {}

    ngOnChanges(changes) {}

    async onFileInput($file) {
        this.file = $file.target.files[0];
        const response = await gedUpload({
            file: this.file,
            fileName: this.file.name,
        });
        this.attachmentId = response.data?.file_id;
        this.name = this.name || this.file.name;
    }

    get isValid() {
        return this.file && this.name;
    }

    async goConfirm() {
        try {
            this.isLoading = true;
            this.message = '';
            await apiRhPvfRequestsMovementsVerticalProgressionsDocumentsPost({
                attachment: this.attachmentId,
                request_id: this.payload.requestId,
                description: this.name,
            });
            this.dialogRef.close({ action: 'refresh' });
        } catch (e) {
            this.message = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
    }

    goBack() {
        this.payload?.close();
    }
}
