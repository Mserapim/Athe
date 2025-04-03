import { Component, Inject, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
    apiRhPvfRequestsIdHistories,
    ApiRhPvfRequestsIdHistoriesResponseItem,
} from 'api/rh/api-rh-pvf-requests-id-histories.service';
import {
    RequestObservationComponent,
    RequestObservationComponentData,
} from '../request-observation/request-observation.component';

@Component({
    selector: 'request-observation-alert',
    templateUrl: './request-observation-alert.component.html',
    standalone: false
})
export class RequestObservationAlertComponent implements OnInit {
    @Input() requestId: number;

    public ultimoHistorico: ApiRhPvfRequestsIdHistoriesResponseItem;

    public titulo = '';
    public texto = '';
    public textoLimite = 150;

    constructor(private dialog: MatDialog) {}

    ngOnInit() {}

    ngOnChanges() {
        this.carregarUltimoHistorico();
    }

    protected async carregarUltimoHistorico() {
        this.ultimoHistorico = null;
        this.titulo = null;
        this.texto = null;

        if (!this.requestId) return;

        const response = await apiRhPvfRequestsIdHistories({
            requestId: this.requestId,
        });

        if (response.total <= 0) return;

        const results = response.results;

        const last = results[results.length - 1];

        this.ultimoHistorico = last;

        if (last.action_label == 'Devolver ao Solicitante') {
            this.titulo =
                'A solicitação foi devolvida pelo aprovador com a seguinte observação';
            this.texto =
                this.ultimoHistorico.observation ||
                'não foi adicionado observação na devolução';
        }
    }

    goDetail() {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestObservationComponent, {
            width: '90%',
            data: <RequestObservationComponentData>{
                observation: this.texto,
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
