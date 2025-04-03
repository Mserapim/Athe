import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { apiRhPvfConfigServerShiftsPermissionsTypes } from 'api/rh/api-rh-pvf-config-server-shifts-permisions-types.service';
import { addDay } from 'utils/add-day';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { PvfConfigRequestsPersonsDataSource } from 'datasources/pvf-config-requests-persons.datasource';
import { PvfConfigServerShiftsEmployeesDataSource } from 'datasources/pvf-config-server-shifts-employees.datasource';
import { PvfConfigServerShiftsWorkplacesDataSource } from 'datasources/pvf-config-server-shifts-workplaces.datasource';
import { Router } from '@angular/router';
import { apiRhPvfScalesServerShiftsPostService } from 'api/rh/api-rh-pvf-scales-server-shifts-post.service';
import { apiRhPvfRequestsIdServerShiftsService } from 'api/rh/api-rh-pvf-requests-id-server-shifts.service';
import { apiRhPvfScalesServerShiftsService } from 'api/rh/api-rh-pvf-scales-server-shifts.service';
import { apiRhPvfScalesServerShiftsIdService } from 'api/rh/api-rh-pvf-scales-server-shifts-id.service';

export class ServerShiftShowComponentData {
    id: number;
    close: () => void;
}

@Component({
    selector: 'app-server-shift-show',
    templateUrl: './server-shift-show.component.html',
    styleUrls: ['./server-shift-show.component.scss'],
    standalone: false
})
export class ServerShiftShowComponent implements OnInit {
    disabled: true;

    dataSourceEmployee: PvfConfigServerShiftsEmployeesDataSource;
    dataSourceWorkplaces: PvfConfigServerShiftsWorkplacesDataSource;

    message: string;
    keywordPerson: string;
    keywordWorkplace: string;

    types = [];

    form = new FormGroup({
        employee: new FormControl<{ pk: number; name: string } | null>(null, [
            Validators.required,
        ]),
        workplace: new FormControl<{ pk: number; name: string } | null>(null, [
            Validators.required,
        ]),
        type: new FormControl<number | null>(null, [Validators.required]),
        start: new FormControl<Date | null>(new Date(), [Validators.required]),
        days: new FormControl<number | null>(1, [Validators.required]),
        end: new FormControl<Date | null>(new Date(), [Validators.required]),
    });

    constructor(
        public dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: ServerShiftShowComponentData,
        private router: Router
    ) {
        this.dataSourceEmployee =
            new PvfConfigServerShiftsEmployeesDataSource();
        this.dataSourceWorkplaces =
            new PvfConfigServerShiftsWorkplacesDataSource();
    }

    ngOnInit() {}

    ngAfterViewInit() {
        this.loadTypes();
        this.load();
    }

    async load() {
        const data = await apiRhPvfScalesServerShiftsIdService({
            id: this.payload.id,
        });

        this.onChangeSearchEmployee(data.employee_name);
        this.onChangeSearchWorkplaces('');

        this.form.setValue({
            days: data.days,
            employee: {
                pk: data.employee,
                name: data.employee_name,
            },
            end: data.end_date,
            start: data.start_date,
            type: data.type_shift,
            workplace: {
                pk: data.workplace,
                name: data.workplace_name,
            },
        });
    }

    async loadTypes() {
        const { results } = await apiRhPvfConfigServerShiftsPermissionsTypes(
            {}
        );
        this.types = results;
    }

    onChangeStartDate($event) {
        this.form.value.start = $event;
        if (!this.form.value.start || !this.form.value.days) return;
        this.form.value.end = addDay(
            this.form.value.start,
            this.form.value.days
        );
    }

    onChangeDays($event) {
        this.form.value.days = $event;
        if (!this.form.value.start || !this.form.value.days) return;
        this.form.value.end = addDay(
            this.form.value.start,
            this.form.value.days
        );
    }

    onSelectEmployee($event) {
        // console.log($event);
        // this.form.value.familyId = $event.pk;
        this.form.controls['employeeId'].setValue($event.pk);
        // console.log(this.form.value);
    }

    onSelectWorkplace($event) {
        // console.log($event);
        // this.form.value.familyId = $event.pk;
        this.form.controls['workplaceId'].setValue($event.pk);
        // console.log(this.form.value);
    }

    onChangeSearchEmployee($event) {
        this.dataSourceEmployee.load({
            keyword: $event,
            page: 1,
            per_page: 10,
        });
    }
    onChangeSearchWorkplaces($event) {
        this.dataSourceWorkplaces.load({
            keyword: $event,
            page: 1,
            per_page: 10,
        });
    }

    displayFn(user: { name: string }): string {
        return user && user.name ? user.name : '';
    }

    async goConfirm() {
        this.message = '';
        try {
            const response = await apiRhPvfScalesServerShiftsPostService({
                // owner: number;
                workplace: this.form.value.workplace?.pk,
                type_shift: this.form.value.type,
                employee: this.form.value.employee?.pk,
                days: this.form.value.days,
                start_date: this.form.value.start,
                end_date: this.form.value.end,
                anexo: null,
                observacao: null
            });
            this.payload.close();
        } catch (e) {
            if (e?.response?.data?.message)
                this.message = e?.response?.data?.message;
            else this.message = 'erro inesperado ao salvar';
        }
    }

    goBack() {
        this.router.navigate(['vdf/server-shifts']);
    }
}
