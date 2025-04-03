import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { apiRetificateObservation } from 'api/rh/api-rh-pvf-requests-id-histories-observation-retification.service';

@Component({
    selector: 'request-show-observation-retification',
    templateUrl: './request-show-observation-retification.component.html',
    standalone: false
})
export class EditObservationModalComponent {
    constructor(
        @Inject(MAT_DIALOG_DATA) public data: any,
        private dialogRef: MatDialogRef<EditObservationModalComponent>
    ) {}

    close() {
        this.dialogRef.close();
    }

    async submitEdit() {
        try {
            const response = await apiRetificateObservation({
                requestId: this.data.pk,
                observation: this.data.observation,
            });
            console.log(response.message);
            this.dialogRef.close(true);
        } catch (error) {
            console.error(error);
        }
    }
}
