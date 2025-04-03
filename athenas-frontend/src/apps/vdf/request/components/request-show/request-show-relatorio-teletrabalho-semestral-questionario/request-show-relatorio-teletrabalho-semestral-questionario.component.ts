import {
    Component,
    EventEmitter,
    Inject,
    Input,
    OnChanges,
    OnInit,
    Output,
} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { printDate } from 'utils/print-date';
import { apiRhPvfApprovalsRequestsIdActions } from 'api/rh/api-rh-pvf-approvals-requests-id-actions.service';
import { ApiRhPvfRequestsIdResponse } from 'api/rh/api-rh-pvf-requests-id.service';
import {
    RhPvfRequestsEnviosRelatorioSemestralTeletrabalhosIdResponse,
    apiRhPvfRequestsEnviosRelatorioSemestralTeletrabalhosIdService,
} from 'api/rh/api-rh-pvf-requests-envios-relatorio-semestral-teletrabalhos-id.service';

@Component({
    selector: 'request-show-relatorio-teletrabalho-semestral-questionario',
    templateUrl: './request-show-relatorio-teletrabalho-semestral-questionario.component.html',
    standalone: false
})
export class RequestShowRelatorioTeletrabalhoSemestralQuestionarioComponent
    implements OnInit, OnChanges
{
    @Input() requestId!: number;
    @Input() request!: ApiRhPvfRequestsIdResponse;
    @Input() showActions!: boolean;

    public actions: any[] = [];
    public dados: RhPvfRequestsEnviosRelatorioSemestralTeletrabalhosIdResponse =
        {};

    printDate = printDate;

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        private dialog: MatDialog
    ) {}

    ngOnInit() {}

    ngOnChanges(changes) {
        this.load({ requestId: this.requestId! }).then();
        this.loadActions({ requestId: this.requestId! }).then();
    }

    protected async load({ requestId }: { requestId: number }) {
        const response =
            await apiRhPvfRequestsEnviosRelatorioSemestralTeletrabalhosIdService(
                {
                    id: requestId,
                }
            );
        this.dados = response;
    }

    protected async loadActions({ requestId }: { requestId: number }) {
        const { results: actions } = await apiRhPvfApprovalsRequestsIdActions({
            requestId,
        });
        this.actions = actions;
    }
}
