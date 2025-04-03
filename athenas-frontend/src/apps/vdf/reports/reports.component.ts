import { Component, OnInit, ViewChild } from '@angular/core';
import { apiRhPvfConfigReportsPaychecksYears } from 'api/rh/api-rh-pvf-config-reports-paychecks-years.service';
import { apiRhPvfConfigReportsTimesheetsYears } from 'api/rh/api-rh-pvf-config-reports-timesheets-years.service';
import { apiRhPvfReportsPointSheet } from 'api/rh/api-rh-pvf-reports-point-sheet.service';
import { apiRhPvfReportsDownload } from 'api/rh/api-rh-pvf-reports-download.service';
import { CurrentUserService } from 'core/current-user/current-user.service';

const now = new Date();

const MONTHS = [
    { value: 1, label: 'JANEIRO' },
    { value: 2, label: 'FEVEREIRO' },
    { value: 3, label: 'MARCO' },
    { value: 4, label: 'ABRIL' },
    { value: 5, label: 'MAIO' },
    { value: 6, label: 'JUNHO' },
    { value: 7, label: 'JULHO' },
];
@Component({
    selector: 'app-reports',
    templateUrl: './reports.component.html',
    styleUrls: ['./reports.component.scss'],
    standalone: false
})
export class ReportsComponent implements OnInit {
    timesheet = {
        options: {
            months: [],
            years: [],
        },
        form: {
            month: now.getFullYear(),
            year: now.getMonth(),
        },
    };

    paycheck = {
        options: {
            months: [],
            years: [],
            type: 0,
        },
        form: {
            month: 0,
            year: 0,
            type: 0,
        },
    };

    filterPaycheck = {
        months: [],
        years: [],
        type: 0,
    };

    formPaycheck = {
        year: 0,
    };

    message: string = '';

    constructor(public currentUserService: CurrentUserService) {}

    ngOnInit() {
        this.loadPaychecksYears();
        this.loadTimesheetMonths();
        this.loadTimesheetYears();
        this.timesheet.form.month = now.getMonth();
        this.timesheet.form.year = now.getFullYear();
    }

    ngAfterViewInit() {}

    async loadPaychecksYears() {
        const { results } = await apiRhPvfConfigReportsPaychecksYears({});
        this.paycheck.options.years = results;
    }

    async loadTimesheetMonths() {
        // const { results } = await apiRhPvfConfigReportsMonths({}); //Dá erro 404
        this.timesheet.options.months = MONTHS;
    }

    async loadTimesheetYears() {
        const { results } = await apiRhPvfConfigReportsTimesheetsYears({});
        this.timesheet.options.years = results;
    }

    async downloadTimesheet() {
        const { uuid } = await apiRhPvfReportsPointSheet({
            ...this.timesheet.form,
        });

        const response = await apiRhPvfReportsDownload({
            uuid,
        });
    }
}
