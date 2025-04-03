import { Component, Inject, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {
    ApiRhPvfRequestsIdUsufructRetificationsResponseItem,
    apiRhPvfRequestsIdUsufructRetificationsService,
} from 'api/rh/api-rh-pvf-requests-id-usufruct-retifications';
import {
    ApiRhPvfRequestsIdUsufructsResponseItem,
    apiRhPvfRequestsIdUsufructs,
} from 'api/rh/api-rh-pvf-requests-id-usufructs.service';

@Component({
    selector: 'request-show-retifications',
    templateUrl: './request-show-retifications.component.html',
    standalone: false
})
export class RequestShowRetificationsComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = ['start_date', 'end_date', 'days'];

    public results: ApiRhPvfRequestsIdUsufructsResponseItem[] = [];
    public resultsBefore: ApiRhPvfRequestsIdUsufructRetificationsResponseItem[] =
        [];

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
        this.load({ requestId: this.requestId! });
        this.loadBefore({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdUsufructs({
            requestId,
        });
        this.results = results;
    }

    protected async loadBefore({ requestId }: { requestId: number }) {
        const { results } =
            await apiRhPvfRequestsIdUsufructRetificationsService({
                requestId,
            });
        this.resultsBefore = results;
    }
}
