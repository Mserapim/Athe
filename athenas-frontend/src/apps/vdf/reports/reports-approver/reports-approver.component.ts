import { Component, OnInit } from '@angular/core';
import { useDownload } from 'api/@base/use-download';
import { apiReportRhPvfApprovers } from 'api/report/api-report-rh-pvf-approvers.service';

@Component({
    selector: 'app-reports-approver',
    templateUrl: './reports-approver.component.html',
    styleUrls: ['../reports.component.scss'],
    standalone: false
})
export class ReportsApproverComponent implements OnInit {
    options = {
        extensions: [
            {
                label: 'Arquivo PDF',
                value: 'PDF',
            },
            {
                label: 'Arquivo XLS',
                value: 'XLS',
            },
        ],
    };

    form = {
        extention: <'PDF' | 'XLS'>'PDF',
    };

    isLoading = false;
    message: string = '';

    constructor() {}

    ngOnInit() {}

    ngAfterViewInit() {}

    get isValid() {
        return true;
    }

    async download() {
        this.isLoading = true;
        const { uuid } = await apiReportRhPvfApprovers({
            extension: this.form.extention,
        });
        try {
            await useDownload(uuid, 0, 5 * 60);
        } finally {
            this.isLoading = false;
        }
    }

    ngOnDestroy() {
        // clearInterval(this.downloadInterval);
    }
}
