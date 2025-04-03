import { Component, OnInit } from '@angular/core';
import { apiRhPvfConfigReportsPaychecksYears } from 'api/rh/api-rh-pvf-config-reports-paychecks-years.service';
import { apiRhPvfConfigReportsTypesPayroll } from 'api/rh/api-rh-pvf-config-reports-types-payroll.service';
import { apiReportRhPvfPaycheckService } from 'api/report/api-report-rh-pvf-paycheck.service';
import { useJasperDownload } from 'api/@base/use-jasper-download';
import { toNumber } from 'lodash-es';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { useDownload } from 'api/@base/use-download';

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
    { value: 13, label: '13º' },
];

@Component({
    selector: 'app-reports-paycheck',
    templateUrl: './reports-paycheck.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsPaycheckComponent implements OnInit {
    options = {
        months: MONTHS,
        years: [],
        types: [],
    };

    form = {
        month: 0,
        year: 0,
        type: 0,
    };

    message: string = '';

    currentMonth: number;
    currentYear: number;

    comp_contracheque: string = '';

    constructor(
        private currentUserService: CurrentUserService,
        private mpPdfPreviewComponent: MpPdfPreviewComponent
    ) {}

    ngOnInit() {
        this.loadPaychecksYears();
    }

    ngAfterViewInit() {}

    async loadPaychecksYears() {
        const { results } = await apiRhPvfConfigReportsPaychecksYears({});
        this.options.years = results;

        this.comp_contracheque =
            this.currentUserService.currentUser.comp_contracheque;

        let mesano = this.comp_contracheque.split('/');

        if (mesano.length == 2) {
            this.form.year = toNumber(mesano[1]);
            this.form.month = toNumber(mesano[0]);

            this.loadConfigReportsTypesPayroll();
        }
    }

    async loadConfigReportsTypesPayroll() {
        const { results } = await apiRhPvfConfigReportsTypesPayroll({
            ...this.form,
        });
        this.options.types = results;
    }

    onChange() {
        if (this.form.month > 0 && this.form.year > 0) {
            this.loadConfigReportsTypesPayroll();
        }
        this.form.type = 0;
    }

    get isValid() {
        return this.form.month > 0 && this.form.year > 0 && this.form.type > 0;
    }

    downloadInterval;

    isLoading: boolean = false;

    async download() {
        this.isLoading = true;
        const { uuid } = await apiReportRhPvfPaycheckService({
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

    ngOnDestroy() {
        clearInterval(this.downloadInterval);
    }
}
