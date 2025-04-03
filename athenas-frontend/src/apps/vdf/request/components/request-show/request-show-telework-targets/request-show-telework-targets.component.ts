import { Component, Inject, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import {
    ApiRhPvfRequestsIdTeleworksTargetsItem,
    apiRhPvfRequestsIdTeleworksTargets,
} from 'api/rh/api-rh-pvf-requests-id-teleworks-targets.service';
import {
    RequestObservationComponent,
    RequestObservationComponentData,
} from '../../request-observation/request-observation.component';
import { useDownload } from 'api/@base/use-download';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { useGedDownload } from 'api/@base/use-ged-download';
import { RequestNewTeleworkStep2DialogComponent } from 'apps/vdf/request/request-new-telework/request-new-telework-step2-dialog/request-new-telework-step2-dialog.component';

@Component({
    selector: 'request-show-telework-targets',
    templateUrl: './request-show-telework-targets.component.html',
    standalone: false
})
export class RequestShowTeleworkTargetsComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = [
        'mark_plan.descricao',
        'mark_plan',
        'saldo_devedor',
        'meta_mes',
        'total_completed',
        'mark_situation',
        'observation',
    ];

    public results: ApiRhPvfRequestsIdTeleworksTargetsItem[] = [];

    constructor(protected router: Router, private dialog: MatDialog) {}

    ngOnInit() {
        this.load({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiRhPvfRequestsIdTeleworksTargets({
            requestId,
        });
        this.results = results;
    }

    async download(anexo_id: string) {
        const link = await useGedDownload(anexo_id);
    }

    explicarDialog(data: any) {
        let dialogRef = this.dialog.open(
            RequestNewTeleworkStep2DialogComponent,
            {
                data,
            }
        );
    }

    goDetail(row?) {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestObservationComponent, {
            width: '90%',
            data: <RequestObservationComponentData>{
                observation: row?.observation || '',
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
