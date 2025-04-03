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
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewAbsenceService } from '../request-new-absence.service';
import { RequestNewAbsenceStep2Component } from '../request-new-absence-step2/request-new-absence-step2.component';
import {
    ApiRhPvfConfigCidsServiceResponseItem,
    apiRhPvfConfigCidsService,
} from 'api/rh/api-rh-config-cids.service';
import { MatDialog } from '@angular/material/dialog';
import {
    RequestPersonNewComponent,
    RequestPersonNewComponentData,
} from '../../components/request-person-new/request-person-new.component';
import { FuseConfirmationService } from '../../../../../@fuse/services/confirmation';

@Component({
    selector: 'request-new-absence-step2-health-license-family',
    templateUrl: './request-new-absence-step2-health-license-family.component.html',
    standalone: false
})
export class RequestNewAbsenceStep2HealthLicenseFamilyComponent extends RequestNewAbsenceStep2Component {
    form = new FormGroup({
        file: new FormControl<File | null>(null, []),
        fileId: new FormControl<number | null>(null, [Validators.required]),
        person: new FormControl<number | Object | null>(null, [
            Validators.required,
        ]),
        degree_kinship: new FormControl<number | null>(null, [
            Validators.required,
        ]),
        start_date: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
        observation: new FormControl<String | null>(null, []),
        days: new FormControl<number | null>(1, [Validators.required]),
        end_date: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
        cidItem: new FormControl<ApiRhPvfConfigCidsServiceResponseItem>(
            undefined,
            []
        ),
    });

    cids: ApiRhPvfConfigCidsServiceResponseItem[] = [];

    constructor(
        stepper: RequestStepperService,
        protected router: Router,
        public dialog: MatDialog,
        currentUserService: CurrentUserService,
        protected requestNewAbsenceService: RequestNewAbsenceService,
        protected confirmationService: FuseConfirmationService
    ) {
        super(
            stepper,
            router,
            currentUserService,
            requestNewAbsenceService,
            confirmationService,
            dialog
        );
    }

    ngOnInit() {
        this.dataSourceDegreeKinshipt =
            new pvfConfigParamsDegreeKinshiptDataSource();
        this.dataSourceDegreeKinshipt.load({ page: 1, per_page: 10 });
        this.dataSourcePersons = new PvfConfigRequestsPersonsDataSource();

        // this.openPersonNew();

        this.dataSourcePersons.load({ page: 1, per_page: 10 });

        this.loadCids();
    }

    protected getPayload() {
        return {
            ...this.form.value,
            person: this.form.value.person['pk'],
            medical_certificate: this.form.value.fileId,
            substitutes: this.requestNewAbsenceService.substitutes,
        };
    }

    dataSourcePersons: PvfConfigRequestsPersonsDataSource;
    dataSourceDegreeKinshipt: pvfConfigParamsDegreeKinshiptDataSource;

    openPersonNew() {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestPersonNewComponent, {
            width: '90%',
            data: <RequestPersonNewComponentData>{
                close: (response) => {
                    if (response) this.onSelectPerson(response);
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

    displayFn(obj) {
        return obj?.name;
    }

    displayFnCid(item: ApiRhPvfConfigCidsServiceResponseItem): string {
        return item && item.description
            ? item.code + ' - ' + item.description
            : '';
    }

    onSelectPerson($event) {
        this.form.controls['person'].setValue($event?.option?.value || $event);
    }

    onChangeSearch($event) {
        if (this.form.value.person instanceof Object) return;
        this.dataSourcePersons.load({
            keyword: this.form.value.person || undefined,
            page: 1,
            per_page: 10,
        });
    }

    async loadCids() {
        const { results } = await apiRhPvfConfigCidsService({
            per_page: 100,
        });
        this.cids = results;
    }
}
