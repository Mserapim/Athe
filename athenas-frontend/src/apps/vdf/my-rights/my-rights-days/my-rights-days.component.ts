import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { apiRhPvfMyRights } from 'api/rh/api-rh-pvf-my-rights.service';
import { apiRhPvfMyRightsAcquisitionPeriodsIdAttachments } from 'api/rh/api-rh-pvf-myrights-acquisition-periods-id-attachments.service';

export class MyRightsDaysComponentData {
    aquisitionPeriodId: number;
    close: () => void;
}

@Component({
    selector: 'app-my-rights-days',
    templateUrl: './my-rights-days.component.html',
    styleUrls: ['./my-rights-days.component.scss'],
    standalone: false
})
export class MyRightsDaysComponent implements OnInit {
    results: any[] = [];

    displayedColumns: string[] = [
        'description',
        'start_date',
        'end_date',
        'days',
        // 'information',
    ];

    constructor(
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: MyRightsDaysComponentData
    ) {}

    ngOnInit() {}

    ngAfterViewInit() {
        this.load();
    }

    async load() {
        const { results } =
            await apiRhPvfMyRightsAcquisitionPeriodsIdAttachments({
                id: this.payload.aquisitionPeriodId,
            });
        this.results = results;
    }

    goClose() {
        this.payload?.close();
    }
}
