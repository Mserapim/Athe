import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import {
    RequestObservationComponent,
    RequestObservationComponentData,
} from '../../request-observation/request-observation.component';
import { useGedDownload } from 'api/@base/use-ged-download';
import {
    apiVdfSolicitacaoHistoricoAnexos,
    ApiVdfSolicitacaoHistoricoAnexosResponseItem,
} from 'api/vdf/api-vdf-solicitacao-historico-anexos.service';

/** @deprecated */
@Component({
    selector: 'request-show-teletrabalho-desbloqueio',
    templateUrl: './request-show-teletrabalho-desbloqueio.component.html',
    standalone: false
})
export class RequestShowTeletrabalhoDesbloqueioComponent implements OnInit {
    @Input() requestId!: number;

    displayedColumns = ['nome_arquivo', 'origem', 'id'];

    public results: ApiVdfSolicitacaoHistoricoAnexosResponseItem[] = [];

    constructor(protected router: Router, private dialog: MatDialog) {}

    ngOnInit() {
        this.load({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiVdfSolicitacaoHistoricoAnexos({
            id_solicitacao: this.requestId,
        });
        this.results = results;
    }

    async download(anexo_id: string) {
        const link = await useGedDownload(anexo_id);
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
