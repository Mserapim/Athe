import { Component, OnInit } from '@angular/core';
import { useDownload } from 'api/@base/use-download';
import { apiRhPvfConfigReportsFinancialStatementYears } from 'api/rh/api-rh-pvf-config-reports-financial-statement-years.service';
import { apiReportRhPvfIncomeStatement } from 'api/report/api-report-rh-pvf-income-statement.service';
import { toNumber } from 'lodash-es';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { apiAuthCurrentUserService } from 'api/auth/api-auth-current-user.service';

@Component({
    selector: 'app-reports-income-statement',
    templateUrl: './reports-income-statement.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsIncomeStatementComponent implements OnInit {
    years: any[] = [];
    typeByPossession: string = '';

    form = {
        year: <number>0,
        type: 'MPMT',
    };

    message: string = '';
    isLoading = false;

    currentYear: number;

    constructor(private mpPdfPreviewComponent: MpPdfPreviewComponent) {}

    async ngOnInit() {
        this.loadPaychecksYears();
        try {
            const currentUser = await apiAuthCurrentUserService({});
            this.typeByPossession = currentUser.type_by_possession;
        } catch (error) {
            console.error('Erro ao obter informações do usuário atual:', error);
        }
    }

    ngAfterViewInit() {}

    async loadPaychecksYears() {
        const { results } = await apiRhPvfConfigReportsFinancialStatementYears(
            {}
        );
        this.years = results?.reverse();

        this.loadCurrentDate();

        this.form.year = this.currentYear;
    }

    onChange() {}

    get isValid() {
        return this.form.year > 0;
    }

    async download() {
        this.isLoading = true;
        this.message = '';
        try {
            const response = await apiReportRhPvfIncomeStatement({
                ...this.form,
            });
            console.log(response);
            if (response) {
                const { uuid } = response;

                const link = await useDownload(uuid, 0, 30, {
                    automaticDownload: false,
                });

                this.mpPdfPreviewComponent.open(link);
            } else if (response.error) {
                this.message = response.error;
            }
        } catch (error) {
            if (
                error.response &&
                error.response.data &&
                error.response.data.message
            ) {
                this.message = error.response.data.message;
            } else {
                this.message = 'Ocorreu um erro ao gerar o relatório.';
            }
        } finally {
            this.isLoading = false;
        }
    }

    ngOnDestroy() {}

    private loadCurrentDate(): void {
        let today: Date = new Date();

        const dd: string = String(today.getDate()).padStart(2, '0');
        const mounth: number = toNumber(
            String(today.getMonth() + 1).padStart(2, '0')
        ); // janeiro é 0
        this.currentYear = today.getFullYear();
    }
}
