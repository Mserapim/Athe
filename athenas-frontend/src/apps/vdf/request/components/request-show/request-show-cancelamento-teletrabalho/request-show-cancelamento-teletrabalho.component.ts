import { Component, Input, OnInit } from '@angular/core';
import { printDate } from 'utils/print-date';
import { apiRhPvfRequestsIdCancelamentosTeletrabalhos } from 'api/rh/api-rh-pvf-requests-id-cancelamentos-teletrabalhos.service';
@Component({
    selector: 'request-show-cancelameno-teletrabalho',
    templateUrl: './request-show-cancelamento-teletrabalho.component.html',
    standalone: false
})
export class RequestShowCancelamentoTeletrabalhoComponent implements OnInit {
    @Input() requestId!: number;
    public results: any[] = [];

    displayedColumns: string[] = [
        'tipo_solicitacao',
        'date',
        'referencia',
        'status',
        'inicio_plano',
        'fim_plano',
    ];

    printDate = printDate;

    constructor() {}

    ngOnInit() {
        this.load({ requestId: this.requestId! }).then();
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results: results } =
            await apiRhPvfRequestsIdCancelamentosTeletrabalhos({
                id: requestId,
            });
        this.results = results;
    }
}
