import {
    Component,
    ComponentFactoryResolver,
    OnInit,
    ViewChild,
} from '@angular/core';
import { apiRhPvfConfigReportsTimesheetsYears } from 'api/rh/api-rh-pvf-config-reports-timesheets-years.service';
import { useDownload } from 'api/@base/use-download';
import { apiReportRhPvfPointSheet } from 'api/report/api-report-rh-pvf-point-sheet.service';
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

@Component({
    selector: 'app-reports-timesheet',
    templateUrl: './reports-timesheet.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsTimesheetComponent implements OnInit {
    options = {
        months: MONTHS,
        years: [],
    };

    form = {
        month: now.getMonth() + 1,
        year: now.getFullYear(),
    };

    message: string = '';
    isLoading = false;

    constructor(private mpPdfPreviewComponent: MpPdfPreviewComponent) {}

    ngOnInit() {
        this.loadPaychecksYears();
    }

    ngAfterViewInit() {}

    async loadPaychecksYears() {
        const { results } = await apiRhPvfConfigReportsTimesheetsYears({});
        this.options.years = results;
    }

    onChange() {
        if (this.form.month > 0 && this.form.year > 0) {
        }
    }

    get isValid() {
        return this.form.month > 0 && this.form.year > 0;
    }

    async download() {
        this.isLoading = true;
        const { uuid } = await apiReportRhPvfPointSheet({
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
}
