import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewAbsenceStep2Component } from '../request-new-absence-step2/request-new-absence-step2.component';
import { RequestNewAbsenceService } from '../request-new-absence.service';
import {
    ApiPvfRequestsAbsencesHealthLicensesPayload,
    apiPvfRequestsAbsencesHealthLicensesService,
} from 'api/rh/api-rh-pvf-requests-absences-health-licenses.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import {
    ApiRhPvfConfigCidsServiceResponseItem,
    apiRhPvfConfigCidsService,
} from 'api/rh/api-rh-config-cids.service';
import {FuseConfirmationService} from "../../../../../@fuse/services/confirmation";
import {MatDialog} from "@angular/material/dialog";

@Component({
    selector: 'request-new-absence-step2-health-license',
    templateUrl: './request-new-absence-step2-health-license.component.html',
    standalone: false
})
export class RequestNewAbsenceStep2HealthLicenseComponent extends RequestNewAbsenceStep2Component {
    protected form = new FormGroup({
        file: new FormControl<number | null>(null, []),
        fileId: new FormControl<number | null>(null, [Validators.required]),
        start_date: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
        days: new FormControl<number | null>(null, []),
        end_date: new FormControl<Date | null>(null, [Validators.required]),
        observation: new FormControl<String | null>(null, []),
        hours: new FormControl<number | null>(1, []),
        mode: new FormControl<string | null>('DAY', []),
        substitutes: new FormControl<Object>([], []),
        cidItem: new FormControl<ApiRhPvfConfigCidsServiceResponseItem>(
            undefined,
            []
        ),
    });

    cids: ApiRhPvfConfigCidsServiceResponseItem[] = [];

    constructor(
        stepper: RequestStepperService,
        protected router: Router,
        currentUserService: CurrentUserService,
        protected requestNewAbsenceService: RequestNewAbsenceService,
        protected confirmationService: FuseConfirmationService,
        protected dialog: MatDialog
    ) {
        super(stepper, router, currentUserService,
            requestNewAbsenceService, confirmationService, dialog);
    }

    ngOnInit() {
        this.loadCids();
    }

    async loadCids($event?) {
        const { results } = await apiRhPvfConfigCidsService({
            per_page: 100,
            keyword: $event?.target?.value,
        });
        this.cids = results;
    }

    displayFn(item: ApiRhPvfConfigCidsServiceResponseItem): string {
        return item && item.description
            ? item.code + ' - ' + item.description
            : '';
    }

    protected getPayload() {
        return <ApiPvfRequestsAbsencesHealthLicensesPayload>{
            ...this.form.value,
            hours:
                this.form.value.mode == 'HOUR'
                    ? this.form.value.hours
                    : undefined,
            medical_certificate: this.form.value.fileId,
            cid: this.form.value.cidItem?.pk,
            substitutes: this.requestNewAbsenceService.substitutes as any,
        };
    }
}
