import { Component, OnInit } from '@angular/core';
import { useDownload } from 'api/@base/use-download';
import { apiReportRhPvfDeliveryPointSheetService } from 'api/report/api-report-rh-pvf-delivery-point-sheet.service';
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

const nowString = new Date().toISOString();
const year = nowString.substring(0, 4);
const month = nowString.substring(5, 7);
const referenceStart = month + '/' + year;

@Component({
    selector: 'app-reports-delivery-point-sheet',
    templateUrl: './reports-delivery-point-sheet.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsDeliveryPointSheetComponent implements OnInit {
    form = {
        reference: <string>referenceStart,
    };

    message: string = '';
    isLoading = false;

    constructor(private mpPdfPreviewComponent: MpPdfPreviewComponent) {}

    ngOnInit() {}

    ngAfterViewInit() {}

    get isValid() {
        return true;
    }

    async download() {
        this.isLoading = true;
        this.message = '';
        let uuid;
        try {
            const response = await apiReportRhPvfDeliveryPointSheetService({
                competence: `${this.form.reference}`,
            });
            uuid = response.uuid;
        } catch (e) {
            this.message = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
        if (!uuid) return;
        try {
            const link = await useDownload(uuid, 0, 5 * 60, {
                automaticDownload: false,
            });

            this.mpPdfPreviewComponent.open(link);
        } finally {
            this.isLoading = false;
        }
    }

    ngOnDestroy() {
        // clearInterval(this.downloadInterval);
    }
}
