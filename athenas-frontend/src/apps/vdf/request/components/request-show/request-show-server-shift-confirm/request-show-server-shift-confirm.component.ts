import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { printDate } from 'utils/print-date';
import {
    ApiRhPvfRequestsIdServerShiftsServiceItem,
    apiRhPvfRequestsIdServerShiftsService,
} from 'api/rh/api-rh-pvf-requests-id-server-shifts.service';
import {useGedDownload, useGedUrl} from "../../../../../../api/@base/use-ged-download";
import {
    RequestObservationComponent,
    RequestObservationComponentData
} from "../../request-observation/request-observation.component";
import {MatDialog} from "@angular/material/dialog";
import {MpPdfPreviewComponent} from "../../../../../../components/mp-pdf-preview/mp-pdf-preview.component";
@Component({
    selector: 'request-show-server-shift-confirm',
    templateUrl: './request-show-server-shift-confirm.component.html',
    standalone: false
})
export class RequestShowServerShiftConfirmComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = [
        'type_shift_label',
        'workplace_name',
        'employee_name',
        'start_date',
        'end_date',
        'days',
        'observacao',
        'anexo',
    ];

    public results: ApiRhPvfRequestsIdServerShiftsServiceItem[] = [];

    constructor(private route: ActivatedRoute,
                protected router: Router,
                private dialog: MatDialog,
                private mpPdfPreviewComponent: MpPdfPreviewComponent) {}

    printDate = printDate;

    async ngOnChanges() {
        this.load({ requestId: this.requestId! });
    }

    ngOnInit() {}

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdServerShiftsService({
            id: requestId,
        });
        this.results = results;
    }

    public async visualizarAnexo(id) {
        // useGedDownload(id);
        const link = await useGedUrl(id);
        this.mpPdfPreviewComponent.open(link);
    }

    goDetail(row?) {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestObservationComponent, {
            width: '90%',
            data: <RequestObservationComponentData>{
                observation: row?.observacao || '',
                close: (response?) => {
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
            }
        });
    }
}
