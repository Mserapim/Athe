import { Component, OnInit } from '@angular/core';
import { apiRhPvfConfigReportsFinancialStatementYears } from 'api/rh/api-rh-pvf-config-reports-financial-statement-years.service';
import { apiReportRhPvfFinancialStatement } from 'api/report/api-report-rh-pvf-financial-statement.service';
import { useDownload } from 'api/@base/use-download';
import { toNumber } from 'lodash-es';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Component({
    selector: 'app-reports-financial-statement',
    templateUrl: './reports-financial-statement.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsFinancialStatementComponent implements OnInit {
    years: any[] = [];

    form = {
        ano_inicial: <number>0,
        ano_final: <number>0,
        matricula: <number>this.currentUserService.currentUser.matricula,
    };

    message: string = '';
    isLoading = false;

    currentYear: number;

    constructor(private mpPdfPreviewComponent: MpPdfPreviewComponent, public currentUserService: CurrentUserService) {}

    ngOnInit() {
        this.loadPaychecksYears();
    }

    ngAfterViewInit() {}

    async loadPaychecksYears() {
        const { results } = await apiRhPvfConfigReportsFinancialStatementYears(
            {}
        );
        this.years = results?.reverse();

        this.loadCurrentDate();

        this.form.ano_inicial = this.currentYear;
        this.form.ano_final = this.currentYear;
    }

    onChange() {}

    get isValid() {
        return (
            this.form.ano_inicial > 0 &&
            this.form.ano_final > 0 &&
            this.form.ano_inicial <= this.form.ano_final
        );
    }

    async download() {
        this.isLoading = true;
        const { uuid } = await apiReportRhPvfFinancialStatement({
            ...this.form,
        });
        try {
            const link = await useDownload(uuid, 0, 5 * 60, {
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
        const month: number = toNumber(
            String(today.getMonth() + 1).padStart(2, '0')
        ); // janeiro é 0
        this.currentYear = today.getFullYear();
    }
}
