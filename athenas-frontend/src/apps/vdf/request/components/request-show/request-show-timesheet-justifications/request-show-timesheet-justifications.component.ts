import { Component, Inject, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import {
    ApiRhPvfRequestsIdTimesheetsJustificationsItem,
    apiRhPvfRequestsIdTimesheetsJustifications,
} from 'api/rh/api-rh-pvf-requests-id-timesheets-justifications.service';
import {
    RequestObservationComponent,
    RequestObservationComponentData,
} from '../../request-observation/request-observation.component';
import { useGedDownload } from 'api/@base/use-ged-download';

@Component({
    selector: 'request-show-timesheet-justifications',
    templateUrl: './request-show-timesheet-justifications.component.html',
    standalone: false
})
export class RequestShowTimesheetJustificationsComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = [
        'reason_type',
        // 'number_hours',
        'start_date',
        'end_date',
        'days',
        'observation',
    ];

    public results: ApiRhPvfRequestsIdTimesheetsJustificationsItem[] = [];
    public hasAnyAttachment: boolean = false;

    constructor(
        private route: ActivatedRoute,
        private dialog: MatDialog,
        protected router: Router
    ) {}

    ngOnInit() {
        this.load({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdTimesheetsJustifications({
            id: requestId,
            cancelado: false,
        });
        this.results = results; //.filter((x) => !x.canceled);

        this.hasAnyAttachment = this.results.some(
            (result) => result.attachment
        );

        if (this.hasAnyAttachment) {
            this.displayedColumns.push('action');
        }
    }

    goDetail(row?) {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestObservationComponent, {
            width: '90%',
            data: <RequestObservationComponentData>{
                observation: row?.observation || '',
                close: (response?) => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
                // this.applyFilter();
            }
        });
    }
    async download(file_id) {
        useGedDownload(file_id);
    }
}
