import { Component, Inject, Input, OnChanges, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { useGedDownload } from 'api/@base/use-ged-download';
import { printDate } from 'utils/print-date';
import { apiRhPvfRequestsIdExerciciosCumulativosSubstituicoes } from 'api/rh/api-rh-pvf-requests-id-exercicios-cumulativos-substituicoes.service';
import { apiRhPvfRequestsIdVerticalProgressionsDocuments } from 'api/rh/api-rh-pvf-requests-id-vertical-progressions-documents.service';
import {
    RequestShowProgressaoVerticalCreateComponent,
    RequestShowProgressaoVerticalCreateComponentData,
} from './request-show-progressao-vertical-create/request-show-progressao-vertical-create.component';
import {
    RequestShowProgressaoVerticalRemoveComponent,
    RequestShowProgressaoVerticalRemoveComponentData,
} from './request-show-progressao-vertical-remove/request-show-progressao-vertical-remove.component';
import { requestStepLabel } from 'enums/request-step.enum';
//33640
@Component({
    selector: 'request-show-progressao-vertical',
    templateUrl: './request-show-progressao-vertical.component.html',
    standalone: false
})
export class RequestShowProgressaoVerticalComponent
    implements OnInit, OnChanges
{
    requestStepLabel = requestStepLabel;

    @Input() requestId!: number;

    printDate = printDate;

    displayedColumns = ['doc_origin', 'description', 'actions'];

    public results: any[] = [];

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        private dialog: MatDialog
    ) {}

    ngOnInit() {
        // this.goRemove({ pk: 1, description: 'teste' });
    }

    ngOnChanges(changes) {
        this.load({ requestId: this.requestId! }).then();
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } =
            await apiRhPvfRequestsIdVerticalProgressionsDocuments({
                id: requestId,
            });

        this.results = results;
    }

    async download(file_id) {
        await useGedDownload(file_id);
    }

    goCreate() {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(
            RequestShowProgressaoVerticalCreateComponent,
            {
                width: '50%',
                data: <RequestShowProgressaoVerticalCreateComponentData>{
                    requestId: this.requestId || '',
                    close: (response?) => {
                        dialogRef.close();
                    },
                },
            }
        );

        dialogRef.afterClosed().subscribe((result) => {
            if (result?.action === 'refresh') {
                this.load({ requestId: this.requestId! }).then();
            }
        });
    }

    goRemove(payload: { pk: number; description: string }) {
        console.log(payload);
        event?.stopPropagation();
        const dialogRef = this.dialog.open(
            RequestShowProgressaoVerticalRemoveComponent,
            {
                width: '50%',
                data: <RequestShowProgressaoVerticalRemoveComponentData>{
                    requestId: this.requestId || '',
                    pk: payload.pk,
                    description: payload.description,
                    close: (response?) => {
                        dialogRef.close();
                    },
                },
            }
        );

        dialogRef.afterClosed().subscribe((result) => {
            this.load({ requestId: this.requestId! }).then();
        });
    }
}
