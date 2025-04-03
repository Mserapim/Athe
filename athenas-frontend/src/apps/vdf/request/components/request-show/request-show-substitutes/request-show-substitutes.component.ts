import { Component, Inject, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {
    ApiRhPvfRequestsIdSubstitutesResponseItem,
    apiRhPvfRequestsIdSubstitutes,
} from 'api/rh/api-rh-pvf-requests-id-substitutes.service';

@Component({
    selector: 'request-show-substitutes',
    templateUrl: './request-show-substitutes.component.html',
    standalone: false
})
export class RequestShowSubstitutesComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = [
        'designation',
        'substitute_name',
        'start_date',
        'end_date',
    ];

    public results: ApiRhPvfRequestsIdSubstitutesResponseItem[] = [];

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
        this.load({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdSubstitutes({
            requestId,
        });
        this.results = results;
    }
}
