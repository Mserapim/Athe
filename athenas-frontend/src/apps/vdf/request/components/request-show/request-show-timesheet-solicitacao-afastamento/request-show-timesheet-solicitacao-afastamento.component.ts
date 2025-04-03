import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {
    ApiVdfSolicitacaoFolhaPontoAfastamentoItem,
    apiVdfSolicitacaoFolhaPontoAfastamento,
} from 'api/vdf/api-vdf-solicitacao-folhaponto-afastamentos.service';

@Component({
    selector: 'request-show-timesheet-solicitacao-afastamento',
    templateUrl: './request-show-timesheet-solicitacao-afastamento.component.html',
    standalone: false
})
export class RequestShowTimesheetSolicitacaoAfastamentoComponent
    implements OnInit
{
    @Input() requestId!: number;

    displayedColumns = [
        'id',
        'data_solicitacao',
        'tipo_solicitacao',
        'situacao',
        'agendamentos',
    ];

    public results: ApiVdfSolicitacaoFolhaPontoAfastamentoItem[] = [];

    constructor(private route: ActivatedRoute, protected router: Router) {}

    ngOnInit() {
        this.load({ requestId: this.requestId! });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } = await apiVdfSolicitacaoFolhaPontoAfastamento({
            id: requestId,
        });

        this.results = results;
    }
}
