import { Component } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { PvfUsufructsAcquisitionPeriodsDataSource } from 'datasources/pvf/usufructs-acquisition-periods.service.datasource';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { PvfConfigRequestsAbsencesTypesDataSource } from 'datasources/pvf-config-requests-absences-types.datasource';
import { ConfigRequestsAbsencesTypesEnum } from 'enums/config-requests-absences-types.enum';
import { apiRhPvfConfigRequestsCancelUsufructs } from 'api/rh/api-rh-pvf-config-requests-cancel-usufructs.service';
import { SelectionModel } from '@angular/cdk/collections';
import { apiRhPvfRequestsIdCancelService } from 'api/rh/api-rh-pvf-requests-id-cancel.service';
import {
    ApiRhPvfConfigRequestsRetificationsUsufructsResponseItem,
    apiRhPvfConfigRequestsRetificationsUsufructs,
} from 'api/rh/api-rh-pvf-config-requests-retifications-usufructs.service';
import { RequestNewRetificationService } from '../request-new-retification.service';

@Component({
    selector: 'request-new-retification-step1',
    templateUrl: './request-new-retification-step1.component.html',
    standalone: false
})
export class RequestNewRetificationStep1Component {
    results: ApiRhPvfConfigRequestsRetificationsUsufructsResponseItem[] = [];
    selection = new SelectionModel<any>(true, []);

    displayedColumns: string[] = [
        'select',
        'start_date',
        'end_date',
        'days',
        'type_activity',
        'start_date_acquisition',
        'type_usufruct',
    ];

    constructor(
        private stepper: RequestStepperService,
        private router: Router,
        private requestNewRetificationService: RequestNewRetificationService
    ) {
        stepper.currentStep = 0;
    }

    ngOnInit() {
        this.loadConfigRequestsCanceables();
    }

    get isValid() {
        return this.selection.selected.length > 0;
    }

    async loadConfigRequestsCanceables() {
        const { results } = await apiRhPvfConfigRequestsRetificationsUsufructs(
            {}
        );
        this.results = results;
    }

    async confirm() {
        const selected = this.selection.selected[0];

        const {} = await apiRhPvfRequestsIdCancelService({
            requestId: selected.pk,
        });
    }

    goNext() {
        this.requestNewRetificationService.usufructs_ids =
            this.selection.selected.map((x) => x.pk);

        let sum = 0;
        this.selection.selected.forEach((x) => (sum += x.days));
        this.requestNewRetificationService.total_days_to_retification = sum;

        this.router.navigate(['vdf/solicitacoes/retificacoes', 'step2']);
    }
}
