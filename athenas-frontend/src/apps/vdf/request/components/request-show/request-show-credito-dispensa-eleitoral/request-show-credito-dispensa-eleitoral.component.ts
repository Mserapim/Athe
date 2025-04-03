import { Component, Inject, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import {
    RequestObservationComponent,
    RequestObservationComponentData,
} from '../../request-observation/request-observation.component';
import { MpPdfPreviewComponent } from 'components/mp-pdf-preview/mp-pdf-preview.component';
import { useGedDownload } from 'api/@base/use-ged-download';
import {
    apiVdfSolicitacaoCreditoEleitoralDetalhes, VdfSolicitacaoCreditoEleitoralDetalhes
} from "../../../../../../api/vdf/api-vdf-solicitacao-credito-dispensa-eleitoral-detalhes.service";

@Component({
    selector: 'request-show-credito-dispensa-eleitoral',
    templateUrl: './request-show-credito-dispensa-eleitoral.component.html',
    standalone: false
})
export class RequestShowCreditoDispensaEleitoralComponent implements OnInit {
    @Input() id!: number;

    displayedColumns = [
        'tipo_solicitacao_display',
        'data_inicio',
        'data_fim',
        'dias',
        'observacao',
    ];



    public results: any[] = [];

    constructor(
        private route: ActivatedRoute,
        private mpPdfPreviewComponent: MpPdfPreviewComponent,
        protected router: Router,
        private dialog: MatDialog
    ) {}

    async ngOnInit() {
        await this.load({id: this.id!});
    }

    protected async load({ id }: { id: number }) {
        const result = await apiVdfSolicitacaoCreditoEleitoralDetalhes({
            id,
        });
        this.results = [result]
    }

    async download(anexo_id: string) {
        const link = await useGedDownload(anexo_id);

        // this.mpPdfPreviewComponent.open(link);
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

    getResults() {
        return this.results;
    }
}
