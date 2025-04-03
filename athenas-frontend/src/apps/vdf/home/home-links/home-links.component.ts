import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { addDay } from 'utils/add-day';
import { apiReportRhPvfPointSheet } from 'api/report/api-report-rh-pvf-point-sheet.service';
import { useDownload } from 'api/@base/use-download';
import { apiReportRhPvfPaycheckService } from 'api/report/api-report-rh-pvf-paycheck.service';
import { useJasperDownload } from 'api/@base/use-jasper-download';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';

@Component({
    selector: 'app-home-links',
    templateUrl: './home-links.component.html',
    standalone: false
})
export class HomeLinksComponent {
    isLoadingTimesheet: boolean;
    isLoadingPaycheck: boolean;
    comp_contracheque: string = '';

    constructor(
        private _router: Router,
        public currentUserService: CurrentUserService,
        private mpPdfPreviewComponent: MpPdfPreviewComponent
    ) {}

    ngOnInit() {
        this.currentUserService.load().then((currenceUser) => {
            this.comp_contracheque = currenceUser?.comp_contracheque;
        });
    }

    async downloadPaycheck() {
        const [month, year] = this.comp_contracheque.split('/').map((x) => +x);
        this.isLoadingPaycheck = true;
        const tipoFolha = 9999 // código para pegar todos os contracheques
        const { uuid } = await apiReportRhPvfPaycheckService({
            year,
            month,
            type: tipoFolha,
        });

        try {
            const link = await useDownload(uuid, 0, 30, {
                automaticDownload: false,
            });

            this.mpPdfPreviewComponent.open(link);
        } finally {
            this.isLoadingPaycheck = false;
        }
    }

    async downloadTimesheet() {
        const [month, year] = this.competence(5)
            .split('/')
            .map((x) => +x);

        this.isLoadingTimesheet = true;
        const { uuid } = await apiReportRhPvfPointSheet({
            year,
            month,
        });
        try {
            const link = await useDownload(uuid, 0, 30, {
                automaticDownload: false,
            });

            this.mpPdfPreviewComponent.open(link);
        } finally {
            this.isLoadingTimesheet = false;
        }
    }

    competence(daycut = 5) {
        let now = new Date();

        if (now.getDate() <= daycut) {
            now = addDay(now, -daycut + 5);
        }

        const str = now.toISOString();
        const month = str.substring(5, 7);
        const year = str.substring(0, 4);
        return `${month}/${year}`;
    }

    tipoFolha(){
        let tipoPosse = this.currentUserService.currentUser.type_by_possession
        switch (tipoPosse) {
            case 'EST':
                return 49
            case 'RES':
                return 63
            default:
                return 1
        }
    }
}
