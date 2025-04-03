import { Component, OnInit, ViewChild } from '@angular/core';
import { apiRhPvfConfigReportsPaychecksYears } from 'api/rh/api-rh-pvf-config-reports-paychecks-years.service';
import { useDownload } from 'api/@base/use-download';
import { apiReportRhPvfCalendar } from 'api/report/api-report-rh-pvf-calendar.service';
import { toNumber } from 'lodash-es';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';

const now = new Date();

const MONTHS = [
    { value: 1, label: 'JANEIRO' },
    { value: 2, label: 'FEVEREIRO' },
    { value: 3, label: 'MARCO' },
    { value: 4, label: 'ABRIL' },
    { value: 5, label: 'MAIO' },
    { value: 6, label: 'JUNHO' },
    { value: 7, label: 'JULHO' },
    { value: 8, label: 'AGOSTO' },
    { value: 9, label: 'SETEMBRO' },
    { value: 10, label: 'OUTUBRO' },
    { value: 11, label: 'NOVEMBRO' },
    { value: 12, label: 'DEZEMBRO' },
];

const TYPES = [
    { value: 1, label: 'Completo' },
    { value: 2, label: 'Resumido' },
];

@Component({
    selector: 'app-reports-calendar',
    templateUrl: './reports-calendar.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsCalendarComponent implements OnInit {
    options = {
        months: MONTHS,
        years: [],
        types: TYPES,
        teams: [],
    };

    form = {
        month: 0,
        year: 0,
        team_id: 0,
        type_report: undefined,
    };

    message: string = '';

    currentMonth: number;
    currentYear: number;

    constructor(private mpPdfPreviewComponent: MpPdfPreviewComponent) {}

    ngOnInit() {
        this.loadPaychecksYears();
    }

    ngAfterViewInit() {}

    async loadPaychecksYears() {
        const { results } = await apiRhPvfConfigReportsPaychecksYears({});
        this.options.years = results;

        this.loadCurrentDate();

        this.form.year = this.currentYear;
        this.form.month = this.currentMonth;
    }

    onChange() {
        if (this.form.month > 0 && this.form.year > 0) {
            // this.loadConfigReportsTypesPayroll();
        }
    }

    get isValid() {
        return (
            this.form.month > 0 &&
            this.form.year > 0 &&
            this.form.type_report > 0
        );
    }

    isLoading = false;

    async download() {
        this.isLoading = true;
        const { uuid } = await apiReportRhPvfCalendar({
            ...this.form,
        });
        try {
            const link = await useDownload(uuid, 0, 30, {
                automaticDownload: false,
            });

            this.mpPdfPreviewComponent.open(link);
        } finally {
            this.isLoading = false;
        }
    }

    ngOnDestroy() {}

    private loadCurrentDate(): void {
        let today: Date = new Date();

        const dd: string = String(today.getDate()).padStart(2, '0');
        this.currentMonth = toNumber(
            String(today.getMonth() + 1).padStart(2, '0')
        ); // janeiro é 0
        this.currentYear = today.getFullYear();
    }
}
