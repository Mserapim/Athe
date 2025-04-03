import { Component, Inject, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {
    ApiRhPvfRequestsIdTimesheetsJustificationsItem,
    apiRhPvfRequestsIdTimesheetsJustifications,
} from 'api/rh/api-rh-pvf-requests-id-timesheets-justifications.service';

@Component({
    selector: 'request-show-timesheet-pendings',
    templateUrl: './request-show-timesheet-pendings.component.html',
    standalone: false
})
export class RequestShowTimesheetPendingsComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = [
        'reason_type',
        'number_hours',
        'start_date',
        'end_date',
        'days',
        'observation',
    ];

    public results: ApiRhPvfRequestsIdTimesheetsJustificationsItem[] = [];

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
        this.load({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdTimesheetsJustifications({
            id: requestId,
        });
        this.results = results;
    }
}
