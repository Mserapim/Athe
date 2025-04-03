import { Component } from '@angular/core';
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { addDay } from 'utils/add-day';
import { addMinute } from 'utils/add-minute';
import { BehaviorSubject, first, map, mergeMap, take } from 'rxjs';
import { pvfUsufructsVacationConfigsDataSource } from 'datasources/pvf/usufructs-vacation-configs.service.datasource';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { PvfConfigRequestsPersonsDataSource } from 'datasources/pvf-config-requests-persons.datasource';
import { pvfRequestsAbsencesHealthLicensesService } from 'services/pvf-requests-absences-health-licenses.service';
import { pvfRequestsAbsencesHealthFamilyLicensesService } from 'services/pvf-requests-absences-health-family-licenses.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { pvfConfigParamsDegreeKinshiptDataSource } from 'datasources/pvf-config-params-degree-kinshipt.datasource';
import { pvfRequestsAbsencesPaternityAbsencesService } from 'services/pvf-requests-absences-health-paternity-absences.service';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { RequestNewAbsenceStep2Component } from '../request-new-absence-step2/request-new-absence-step2.component';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewAbsenceService } from '../request-new-absence.service';
import { FuseConfirmationService } from '../../../../../@fuse/services/confirmation';
import { MatDialog } from '@angular/material/dialog';

@Component({
    selector: 'request-new-absence-step2-blood-donation',
    templateUrl: './request-new-absence-step2-blood-donation.component.html',
    standalone: false
})
export class RequestNewAbsenceStep2BloodDonationComponent extends RequestNewAbsenceStep2Component {
    form = new FormGroup({
        file: new FormControl<File | null>(null, []),
        fileId: new FormControl<number | null>(null, [Validators.required]),
        start_date: new FormControl<Date | null>(null, [Validators.required]),
        days: new FormControl<number>(1, [Validators.required]),
        end_date: new FormControl<Date | null>(null, []),
        observation: new FormControl<string>('', []),
    });

    constructor(
        stepper: RequestStepperService,
        protected router: Router,
        currentUserService: CurrentUserService,
        protected requestNewAbsenceService: RequestNewAbsenceService,
        protected confirmationService: FuseConfirmationService,
        protected dialog: MatDialog
    ) {
        super(
            stepper,
            router,
            currentUserService,
            requestNewAbsenceService,
            confirmationService,
            dialog
        );
        if (!this.requestNewAbsenceService.typeId) this.goBack();
    }

    protected getPayload() {
        return {
            ...this.form.value,
            days: undefined,
            end_date: this.form.value.start_date,
            blood_donation_certificate: this.form.value.fileId,
            substitutes: this.requestNewAbsenceService.substitutes,
        };
    }

    ngOnInit() {}

    ngAfterInitView() {
        this.onChangeStartDate(new Date());
    }
}
