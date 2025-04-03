import {
    Component,
    Input,
    OnChanges,
    OnInit,
    ViewChild,
    AfterViewInit,
    ElementRef,
    ChangeDetectorRef,
} from '@angular/core';
import { MatTable } from '@angular/material/table';
import { ActivatedRoute, Router } from '@angular/router';
import { useGedDownload } from 'api/@base/use-ged-download';
import { printDate } from 'utils/print-date';
import { apiRhPvfRequestsIdHozirontalProgressionsDocuments } from 'api/rh/api-rh-pvf-requests-id-horizontal-progressions-documents.service';
import {
    ApiRhPvfRequestsIdResponse,
    apiRhPvfRequestsId,
} from 'api/rh/api-rh-pvf-requests-id.service';
import { apiRhPvfRequestsMovementsHorizontalProgressionsDocumentsDelete } from 'api/rh/api-rh-pvf-requests-movements-horizontal-progressions-documents-id-delete.service';

@Component({
    selector: 'request-show-horizontal-progressions',
    templateUrl: './request-show-horizontal-progressions.component.html',
    standalone: false
})
export class RequestShowHorizontalProgressionsComponent
    implements OnInit, OnChanges
{
    @Input() requestId!: number;

    printDate = printDate;

    displayedColumns: string[] = [
        'description',
        'doc_origin_display',
        'attachment',
        'delete',
    ];

    public results: any[] = [];

    isAguardandoEnvio: boolean = false;
    documents: any[] = [];
    file: any;
    requestDetails: ApiRhPvfRequestsIdResponse;

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
        this.loadRequestDetails();
    }

    ngOnChanges(changes) {
        this.load({ requestId: this.requestId! }).then();
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } =
            await apiRhPvfRequestsIdHozirontalProgressionsDocuments({
                id: requestId,
            });

        this.results = results;
    }

    async download(file_id) {
        await useGedDownload(file_id);
    }

    async loadRequestDetails() {
        try {
            this.requestDetails = await apiRhPvfRequestsId({
                requestId: this.requestId,
            });
            this.isAguardandoEnvio =
                this.requestDetails &&
                this.requestDetails.status_name === 'Aguardando Envio';
        } catch (error) {
            console.error('Erro ao obter os detalhes da requisição:', error);
            this.isAguardandoEnvio = false;
        }
    }

    @ViewChild(MatTable) table: MatTable<any>;
    async removerItem(element) {
        try {
            await apiRhPvfRequestsMovementsHorizontalProgressionsDocumentsDelete(
                { id: element.pk }
            );

            this.results = this.results.filter(
                (item) => item.pk !== element.pk
            );

            if (this.table) {
                this.table.renderRows();
            }
        } catch (error) {
            console.error('Erro ao deletar o item:', error);
        }
    }
}
