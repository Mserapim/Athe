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
import { apiRhPvfRequestsIdExerciciosCumulativosSubstituicoes } from 'api/rh/api-rh-pvf-requests-id-exercicios-cumulativos-substituicoes.service';
import { RequestIndeferirDialog } from '../../request-indeferir-dialog/request-indeferir-dialog.component';
import { apiRhPvfApprovalsRequestsIdActions } from 'api/rh/api-rh-pvf-approvals-requests-id-actions.service';
import {
    ApiRhPvfRequestsIdResponse,
    apiRhPvfRequestsId,
} from 'api/rh/api-rh-pvf-requests-id.service';
import { apiRhPvfApprovalsRequestsId } from 'api/rh/api-rh-pvf-approvals-requests-id.service';
import { AtualizarExercicioCumulativoService } from './request-show-exercicio-cumulativo.service';
import { apiRhPvfRequestsIdExerciciosCumulativosDiasConsolidados } from 'api/rh/api-rh-pvf-requests-id-exercicios-cumulativos-dias-consolidados.service';

@Component({
    selector: 'request-show-exercicio-cumulativo',
    templateUrl: './request-show-exercicio-cumulativo.component.html',
    standalone: false
})
export class RequestShowExercicioCumulativoComponent
    implements OnInit, OnChanges
{
    @Input() requestId!: number;
    @Input() request!: ApiRhPvfRequestsIdResponse;
    @Input() showActions!: boolean;
    @Output() changeRequest = new EventEmitter<ApiRhPvfRequestsIdResponse>();

    public actions: any[] = [];
    public results: any[] = [];
    public diasCons: number = 0;
    public diasConsolidados: boolean = false;

    printDate = printDate;

    displayedColumns = [
        'cumulativa',
        'serv_substituto',
        'serv_substituido',
        'data_inicio',
        'data_fim',
        'status_label',
        'act_indefer',
    ];

    constructor(
        private route: ActivatedRoute,
        protected router: Router,
        private dialog: MatDialog,
        private eventExercicioCumulativo: AtualizarExercicioCumulativoService
    ) {}

    ngOnInit() {
        this.eventExercicioCumulativo.getEvent().subscribe((event) => {
            if (event.event === 'atualizarExercicioCumulativo') {
                this.results = event.data;
                if (this.results.length > 0) {
                    const even = (element) => element.dias_consolidados > 0;
                    this.diasConsolidados = this.results.some(even);
                }
            }
        });
    }

    ngOnChanges(changes) {
        this.load({ requestId: this.requestId! }).then();
        this.loadActions({ requestId: this.requestId! }).then();
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } =
            await apiRhPvfRequestsIdExerciciosCumulativosSubstituicoes({
                id: requestId,
            });
        this.results = results;
        this.loadDiasConsolidados(results).then();
    }

    protected async loadDiasConsolidados(results) {
        if (results.length > 0) {
            const even = (element) => element.dias_consolidados > 0;
            this.diasConsolidados = this.results.some(even);
            const resDiasCons =
                await apiRhPvfRequestsIdExerciciosCumulativosDiasConsolidados({
                    id: this.requestId,
                });
            this.diasCons = resDiasCons.dias_consolidados;
        }
    }

    protected async loadActions({ requestId }: { requestId: number }) {
        const { results: actions } = await apiRhPvfApprovalsRequestsIdActions({
            requestId,
        });
        this.actions = actions;
    }

    doIndefer(itemId: number) {
        const dialogRef = this.dialog.open(RequestIndeferirDialog, {
            width: '700px',
            data: { itemId },
        });
        dialogRef.afterClosed().subscribe((result) => {
            this.load({ requestId: this.requestId! }).then();
            this.loadActions({ requestId: this.requestId! }).then();
            this.dochangeRequest({ requestId: this.requestId! });
        });
    }

    async dochangeRequest({ requestId }: { requestId: number }) {
        const response = await apiRhPvfApprovalsRequestsId({
            requestId,
        });
        this.changeRequest.emit(response);
    }
}
