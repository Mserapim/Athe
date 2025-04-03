import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { PvfConfigRequestsPersonsDataSource } from 'datasources/pvf-config-requests-persons.datasource';
import { pvfConfigParamsDegreeKinshiptDataSource } from 'datasources/pvf-config-params-degree-kinshipt.datasource';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewAbsenceService } from '../request-new-absence.service';
import { RequestNewAbsenceStep2Component } from '../request-new-absence-step2/request-new-absence-step2.component';
import { MatDialog } from '@angular/material/dialog';
import {
    RequestPersonNewComponent,
    RequestPersonNewComponentData,
} from '../../components/request-person-new/request-person-new.component';
import {FuseConfirmationService} from "../../../../../@fuse/services/confirmation";

@Component({
    selector: 'request-new-absence-step2-mourning',
    templateUrl: './request-new-absence-step2-mourning.component.html',
    standalone: false
})
export class RequestNewAbsenceStep2MourningComponent extends RequestNewAbsenceStep2Component {
    dataSourcePersons = new PvfConfigRequestsPersonsDataSource();
    dataSourceDegreeKinshipt = new pvfConfigParamsDegreeKinshiptDataSource();

    form = new FormGroup({
        file: new FormControl<File | null>(null, []),
        fileId: new FormControl<number | null>(null, [Validators.required]),
        person: new FormControl<number | Object | null>(null, [
            Validators.required,
        ]),
        family_bond: new FormControl<number | null>(null, [
            Validators.required,
        ]),
        start_date: new FormControl<Date | null>(null, [Validators.required]),
        days: new FormControl<number | null>(8, [Validators.required]),
        end_date: new FormControl<Date | null>(null, [Validators.required]),
    });

    constructor(
        stepper: RequestStepperService,
        protected router: Router,
        public dialog: MatDialog,
        currentUserService: CurrentUserService,
        protected requestNewAbsenceService: RequestNewAbsenceService,
        protected confirmationService: FuseConfirmationService
    ) {
        super(stepper, router, currentUserService,
            requestNewAbsenceService, confirmationService, dialog);

    }

    protected getPayload() {
        return {
            ...this.form.value,
            person: this.form.value.person['pk'],
            death_certificate: this.form.value.fileId,
            substitutes: this.requestNewAbsenceService.substitutes,
        };
    }

    displayFn(obj) {
        return obj?.name;
    }

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

    onSelectPerson($event) {
        this.form.controls['person'].setValue($event?.option?.value || $event);
    }

    onChangeSearch($event) {
        if (this.form.value.person instanceof Object) return;
        console.log(this.form.value.person);
        this.dataSourcePersons.load({
            keyword: this.form.value.person || undefined,
            page: 1,
            per_page: 10,
        });
    }

    ngOnInit() {
        this.dataSourceDegreeKinshipt =
            new pvfConfigParamsDegreeKinshiptDataSource();
        this.dataSourceDegreeKinshipt.load({ page: 1, per_page: 10 });
        this.dataSourcePersons = new PvfConfigRequestsPersonsDataSource();
        this.dataSourcePersons.load({ page: 1, per_page: 10 });
    }

    ngAfterInitView() {
        this.onChangeStartDate(new Date());
    }
}
